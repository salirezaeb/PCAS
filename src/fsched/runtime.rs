use std::future::Future;
use std::sync::Arc;

use tokio::sync::Mutex;
use tokio::task::JoinHandle;

use super::process::Process;

#[derive(Clone)]
pub struct Runtime {
    pub tasks: Arc<Mutex<Vec<JoinHandle<()>>>>,
}

impl Runtime {
    pub fn new() -> Self {
        Runtime {
            tasks: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub async fn task_count(&self) -> usize {
        let tasks = self.tasks.lock().await;
        tasks.len()
    }

    pub async fn add_task<F>(&self, task: F)
    where
        F: Future<Output = ()> + Send + 'static,
    {
        let handle = tokio::spawn(task);
        let mut tasks = self.tasks.lock().await;
        tasks.push(handle);
    }

    pub async fn add_function<F, Fut>(&self, f: F)
    where
        F: FnOnce() -> Fut + Send + Sync + 'static,
        Fut: std::future::Future<Output = ()> + Send + 'static,
    {
        self.add_task(async move {
            f().await;
        }).await;
    }

    pub async fn add_process(&self, mut process: Process) {
        self.add_task(async {
            process.run();

            match process.child {
                Ok(_) => {
                    println!("{:#?}", process.capture_output().await);
                }
                Err(e) => {
                    eprintln!("Failed to launch process: {}", e);
                }
            }
        }).await;
    }

    pub async fn remove_completed_tasks(&self) {
        let mut tasks = self.tasks.lock().await;
        tasks.retain(|handle| !handle.is_finished());
    }

    pub async fn daemon(&self) {
        loop {
            self.remove_completed_tasks().await;
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }
    }
}


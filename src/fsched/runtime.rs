use std::io::{Error, ErrorKind};
use std::future::Future;
use std::sync::Arc;

use tokio::sync::{oneshot, Mutex};
use tokio::task::JoinHandle;

use super::process::{Process, ProcessResult};

#[derive(Clone)]
pub struct Runtime {
    pub tasks: Arc<Mutex<Vec<JoinHandle<()>>>>,
    daemons: Arc<Mutex<Vec<JoinHandle<()>>>>,
}

impl Runtime {
    pub fn new() -> Self {
        Runtime {
            tasks: Arc::new(Mutex::new(Vec::new())),
            daemons: Arc::new(Mutex::new(Vec::new())),
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

    pub async fn run_process(&self, mut process: Process) -> Result<ProcessResult, Error> {
        let (tx, rx) = oneshot::channel();

        self.add_task(async {
            process.run();

            match process.child {
                Ok(_) => {
                    let _ = tx.send(Ok(process.capture_output().await));
                }
                Err(e) => {
                    let _ = tx.send(Err(e));
                }
            }
        }).await;

        match rx.await {
            Ok(res) => res,
            Err(_) => Err(Error::new(ErrorKind::Other, "Failed to read from channel")),
        }
    }

    pub async fn remove_completed_tasks(&self) {
        let mut tasks = self.tasks.lock().await;
        tasks.retain(|handle| !handle.is_finished());
    }

    pub async fn daemon_count(&self) -> usize {
        let tasks = self.daemons.lock().await;
        tasks.len()
    }

    pub async fn add_daemon<F, Fut>(&self, daemon: F)
    where
        F: FnOnce() -> Fut + Send + Sync + 'static,
        Fut: std::future::Future<Output = ()> + Send + 'static,
    {
        let handle = tokio::spawn(async move {
            daemon().await;
        });

        let mut daemons = self.daemons.lock().await;
        daemons.push(handle);
    }

    pub async fn daemon(&self) {
        loop {
            self.remove_completed_tasks().await;
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }
    }
}


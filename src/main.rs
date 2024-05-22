mod sysfo;

use std::process::Stdio;

use sysfo::lib::export_system_info;

use serde::{Serialize, Deserialize};
use tokio::io::{self};
use tokio::process::Command;
use tokio::task::JoinHandle;
use tokio::time::Duration;

#[derive(Debug, Deserialize, Serialize)]
struct ProcessResult {
    pid: u32,
    exit_status: i32,
    stdout: String,
    stderr: String,
}

#[tokio::main]
async fn main() -> io::Result<()> {
    let scrape_interval = Duration::from_secs(30);

    let mut tasks = vec![];

    let commands = vec![
        "sleep 5",
        "echo hello, world!",
        "ls -lah",
        "sleep 1 && echo pagh",
    ];

    sysfo::lib::launch_exporter(scrape_interval, &mut tasks);

    for command in commands {
        launch_task(command.to_string(), &mut tasks)
    }

    for task in tasks {
        if let Err(e) = task.await {
            eprintln!("Error executing task: {:?}", e);
        }
    }

    Ok(())
}

fn launch_task(command: String, tasks: &mut Vec<JoinHandle<()>>) {
    let task = tokio::spawn(async move {
        match launch_process(command).await {
            Ok(child) => {
                println!("{:#?}", manage_process(child).await);
            }
            Err(e) => {
                eprintln!("Failed to launch process: {}", e);
            }
        }
    });

    tasks.push(task);
}

async fn launch_process(command: String) -> io::Result<tokio::process::Child> {
    let mut parts = command.split_whitespace();
    let program = parts.next().unwrap();
    let args: Vec<&str> = parts.collect();

    Command::new(program)
            .args(&args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
}

async fn manage_process(child: tokio::process::Child) -> ProcessResult {
    let pid = child.id().unwrap_or_default();
    let output = child.wait_with_output().await.unwrap_or_else(|e| {
        eprintln!("Failed to wait on process: {}", e);
        std::process::Output {
            status: std::process::ExitStatus::default(),
            stdout: Vec::new(),
            stderr: Vec::new(),
        }
    });

    ProcessResult {
        pid,
        exit_status: output.status.code().unwrap_or_default(),
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
    }
}


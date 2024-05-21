use std::process::Stdio;
use tokio::process::Command;
use tokio::io::{self};
use serde::{Serialize, Deserialize};


#[derive(Debug, Deserialize, Serialize)]
struct ProcessResult {
    pid: u32,
    exit_status: i32,
    stdout: String,
    stderr: String,
}

#[tokio::main]
async fn main() -> io::Result<()> {
    let commands = vec![
        "sleep 5",
        "echo hello, world!",
        "ls -lah",
        "sleep 1 && echo pagh",
    ];

    let mut tasks = vec![];

    for command in commands {
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

    for task in tasks {
        if let Err(e) = task.await {
            eprintln!("Error executing task: {:?}", e);
        }
    }

    println!("All processes have terminated.");
    Ok(())
}

async fn launch_process(command: &str) -> io::Result<tokio::process::Child> {
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


use std::io::{Error, ErrorKind};
use std::process::Stdio;

use serde::{Serialize, Deserialize};
use tokio::io::{self};
use tokio::process::Command;

#[derive(Debug, Deserialize, Serialize)]
pub struct ProcessResult {
    command: String,
    // timestamp: ?
    pid: Option<u32>,
    stdout: Option<String>,
    stderr: Option<String>,
    exit_status: Option<i32>,
}

pub struct Process {
    pub child: io::Result<tokio::process::Child>,
    result: ProcessResult,
}

impl Process {
    pub fn new(command: String) -> Self {
        let result = ProcessResult {
            pid: None,
            stdout: None,
            stderr: None,
            exit_status: None,
            command: command.clone(),
        };

        Self {
            result,
            child: Err(Error::new(ErrorKind::Other, "Failed to create process")),
        }
    }

    pub fn run(&mut self) {
        let command = self.result.command.clone();

        let mut parts = command.split_whitespace();
        let program = parts.next().unwrap();
        let args: Vec<&str> = parts.collect();

        let child = Command::new(program)
                            .args(&args)
                            .stdout(Stdio::piped())
                            .stderr(Stdio::piped())
                            .spawn();

        self.child = child;

        if let Ok(child) = &self.child {
            self.result.pid = child.id();
        }
    }

    pub async fn capture_output(mut self) -> ProcessResult {
        if let Ok(child) = self.child {
            let output = child.wait_with_output().await.unwrap();

            self.result.stdout = Some(String::from_utf8_lossy(&output.stdout).to_string());
            self.result.stderr = Some(String::from_utf8_lossy(&output.stderr).to_string());
            self.result.exit_status = output.status.code();
        }

        self.result
    }
}


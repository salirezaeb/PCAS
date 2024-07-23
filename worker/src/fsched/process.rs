use std::io::{Error, ErrorKind};
use std::process::Stdio;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde::Serialize;
use tokio::io::{self};
use tokio::process::Command;
use uuid::Uuid;

#[derive(Debug, Serialize)]
pub struct ProcessResult {
    id: Uuid,
    command: String,
    pid: Option<u32>,
    stdout: Option<String>,
    stderr: Option<String>,
    exit_status: Option<i32>,
    timestamp: Option<Duration>,
    execution_time: Option<Duration>,
}

pub struct Process {
    pub cos: u8,
    pub child: io::Result<tokio::process::Child>,
    result: ProcessResult,
}

impl Process {
    pub fn new(command: String, cos: u8) -> Self {
        let result = ProcessResult {
            id: Uuid::new_v4(),
            pid: None,
            stdout: None,
            stderr: None,
            exit_status: None,
            timestamp: None,
            execution_time: None,
            command,
        };

        Self {
            cos,
            result,
            child: Err(Error::new(ErrorKind::Other, "Failed to create process")),
        }
    }

    pub fn run(&mut self) {
        let command = self.result.command.clone();

        let mut parts = command.split_whitespace();
        let program = parts.next().unwrap();
        let args: Vec<&str> = parts.collect();

        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap();

        self.result.timestamp = Some(now);

        let child = Command::new(program)
            .args(&args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn();

        self.child = child;

        if let Ok(child) = &self.child {
            self.result.pid = child.id();
        }

        if self.cos != 0 {
            let cache_alloc_cmd = format!("sudo pqos -I -a pid:{}={}", self.cos, self.result.pid.unwrap());

            let mut parts = cache_alloc_cmd.split_whitespace();
            let program = parts.next().unwrap();
            let args: Vec<&str> = parts.collect();

            let _ = Command::new(program)
                .args(&args)
                .spawn();
        }
    }

    pub async fn capture_output(mut self) -> ProcessResult {
        if let Ok(child) = self.child {
            let output = child.wait_with_output().await.unwrap();

            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap();

            self.result.execution_time = now.checked_sub(self.result.timestamp.unwrap());
            self.result.stdout = Some(String::from_utf8_lossy(&output.stdout).to_string());
            self.result.stderr = Some(String::from_utf8_lossy(&output.stderr).to_string());
            self.result.exit_status = output.status.code();
        }

        self.result
    }
}


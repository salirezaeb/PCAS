use std::sync::Arc;

use axum::{
    extract::{State, Json},
    http::StatusCode,
    response::IntoResponse,
};
use serde::Deserialize;

use super::process::Process;
use super::runtime::Runtime;

#[derive(Deserialize, Debug)]
pub struct TaskRequest {
    command: String,
}

#[derive(Clone)]
pub struct TaskService {
    pub runtime: Arc<Runtime>,
}

impl TaskService {
    pub fn new(runtime: Runtime) -> Self {
        TaskService {
            runtime: Arc::new(runtime),
        }
    }

    pub async fn count_handler(State(state): State<TaskService>) -> impl IntoResponse {
        let count = state.runtime.task_count().await;

        format!("Number of tasks: {}", count)
    }

    pub async fn new_handler(State(state): State<TaskService>, Json(payload): Json<TaskRequest>) -> impl IntoResponse {
        let proc = Process::new(payload.command);

        state.runtime.add_process(proc).await;

        StatusCode::OK
    }
}

#[derive(Clone)]
pub struct DaemonService {
    pub runtime: Arc<Runtime>,
}

impl DaemonService {
    pub fn new(runtime: Runtime) -> Self {
        DaemonService {
            runtime: Arc::new(runtime),
        }
    }

    pub async fn count_handler(State(state): State<DaemonService>) -> impl IntoResponse {
        let count = state.runtime.daemon_count().await;

        format!("Number of tasks: {}", count)
    }
}

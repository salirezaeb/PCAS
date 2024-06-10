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
pub struct HTTPService {
    pub runtime: Arc<Runtime>,
}

impl HTTPService {
    pub fn new(runtime: Runtime) -> Self {
        HTTPService {
            runtime: Arc::new(runtime),
        }
    }

    pub async fn count_handler(State(state): State<HTTPService>) -> impl IntoResponse {
        let count = state.runtime.task_count().await;

        format!("Number of tasks: {}", count)
    }

    pub async fn new_handler(State(state): State<HTTPService>, Json(payload): Json<TaskRequest>) -> impl IntoResponse {
        let proc = Process::new(payload.command);

        state.runtime.add_process(proc).await;

        StatusCode::OK
    }
}

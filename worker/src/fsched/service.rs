use std::sync::Arc;

use axum::{
    extract::{State, Json, Multipart},
    http::StatusCode,
    response::IntoResponse,
};
use serde::{Serialize, Deserialize};
use uuid::Uuid;

use super::process::Process;
use super::runtime::Runtime;

#[derive(Deserialize, Debug)]
pub struct TaskRequest {
    cos: Option<u8>,
    command: Option<String>,
    filename: Option<String>,
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

    pub async fn command_handler(State(state): State<TaskService>, Json(payload): Json<TaskRequest>) -> impl IntoResponse {
        if let Some(command) = payload.command {
            // FIXME: i dont know if it's safe to put zero here
            let proc = Process::new(command, 0);

            match state.runtime.run_process(proc).await {
                Ok(res) => Json(res).into_response(),
                Err(_) => StatusCode::INTERNAL_SERVER_ERROR.into_response(),
            }
        } else {
            StatusCode::BAD_REQUEST.into_response()
        }
    }

    pub async fn new_file_handler(State(state): State<TaskService>, mut multipart: Multipart) -> impl IntoResponse {
        if let Ok(Some(mut field)) = multipart.next_field().await {
            let filename = Uuid::new_v4().to_string();

            while let Ok(Some(chunk)) = field.chunk().await {
                let res = state.runtime.create_file(filename.clone(), chunk.as_ref()).await;

                if let Err(_) = res {
                    return StatusCode::INTERNAL_SERVER_ERROR.into_response();
                }
            }

            #[derive(Serialize)]
            struct Response {
                id: String,
            }

            let response = Response { id: filename };

            return (StatusCode::OK, Json(response)).into_response();
        }

        StatusCode::BAD_REQUEST.into_response()
    }

    pub async fn run_file_handler(State(state): State<TaskService>, Json(payload): Json<TaskRequest>) -> impl IntoResponse {
        match (payload.cos, payload.command, payload.filename) {
            (Some(cos), Some(command), Some(filename)) => {
                match state.runtime.run_file_with_command(command, filename, cos).await {
                    Ok(res) => Json(res).into_response(),
                    Err(_) => StatusCode::INTERNAL_SERVER_ERROR.into_response(),
                }
            },
            _ => StatusCode::BAD_REQUEST.into_response()
        }
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

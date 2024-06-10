use std::sync::Arc;

use axum::{
    extract::State,
    response::IntoResponse,
};
use tokio::sync::Mutex;

use super::runtime::Runtime;

#[derive(Clone)]
pub struct HTTPService {
    pub runtime: Arc<Mutex<Runtime>>,
}

impl HTTPService {
    pub fn new(runtime: Runtime) -> Self {
        let runtime = Arc::new(Mutex::new(runtime));

        HTTPService {
            runtime,
        }
    }

    pub async fn info_handler(State(state): State<HTTPService>) -> impl IntoResponse {
        let mut runtime = state.runtime.lock().await;
        let info = runtime.export_info().await;

        format!("System info: {:?}", info)
    }
}

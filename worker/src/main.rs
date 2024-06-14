mod sysfo;
mod fsched;

use axum::{
    routing::{get, post},
    Router,
};

use fsched::{
    runtime::Runtime as FschedRuntime,
    service::{DaemonService, TaskService},
};
use sysfo::{
    runtime::Runtime as SysfoRuntime,
    service::HTTPService as SysfoService,
};

#[tokio::main]
async fn main() {
    let fsched = FschedRuntime::new();

    let sysfo = SysfoRuntime::new();

    let runtime = fsched.clone();
    fsched.add_daemon(|| async move {
        let task_state = TaskService::new(runtime.clone());

        let task_app = Router::new()
            .route("/new", post(TaskService::new_handler))
            .route("/count", get(TaskService::count_handler))
            .with_state(task_state);

        let daemon_state = DaemonService::new(runtime.clone());

        let daemon_app = Router::new()
            .route("/count", get(DaemonService::count_handler))
            .with_state(daemon_state);

        let exporter_state = SysfoService::new(sysfo);

        let exporter_app = Router::new()
            .route("/info", get(SysfoService::info_handler))
            .with_state(exporter_state);

        let app = Router::new()
            .nest("/task", task_app)
            .nest("/daemon", daemon_app)
            .nest("/system", exporter_app);

        let listener = tokio::net::TcpListener::bind("localhost:3000").await.unwrap();
        axum::serve(listener, app).await.unwrap();
    }).await;

    fsched.daemon().await;
}

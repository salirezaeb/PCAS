mod sysfo;
mod fsched;

use axum::{
    routing::{get, post},
    Router,
};

use config::{Config, FileFormat, File};

use fsched::{
    runtime::Runtime as FschedRuntime,
    service::{DaemonService, TaskService},
};
use sysfo::{
    runtime::Runtime as SysfoRuntime,
    service::HTTPService as SysfoService,
};

const CONFIG_FILE: &str = "config";

#[tokio::main]
async fn main() {
    let app_config = Config::builder()
        .add_source(File::new(CONFIG_FILE, FileFormat::Toml))
        .build()
        .unwrap();

    let fsched = FschedRuntime::new().expect("Failed to create fsched runtime");

    let free_cache = app_config.get("free_cache").unwrap();
    let total_cache = app_config.get("total_cache").unwrap();

    let sysfo = SysfoRuntime::new((free_cache, total_cache));

    let runtime = fsched.clone();
    fsched.add_daemon(|| async move {
        let task_state = TaskService::new(runtime.clone());

        let task_app = Router::new()
            .route("/count", get(TaskService::count_handler))
            .route("/command", post(TaskService::command_handler))
            .route("/file/new", post(TaskService::new_file_handler))
            .route("/file/run", post(TaskService::run_file_handler))
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

        let server_host = app_config.get_string("server_host").unwrap();

        let listener = tokio::net::TcpListener::bind(server_host).await.unwrap();
        axum::serve(listener, app).await.unwrap();
    }).await;

    fsched.daemon().await;
}

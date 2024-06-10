mod sysfo;
mod fsched;

use axum::{
    routing::{get, post},
    Router,
};

use fsched::{
    runtime::Runtime as FschedRuntime,
    service::HTTPService as FschedService,
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
    fsched.add_function(|| async move {
        let fsched_svc = FschedService::new(runtime);

        let task_app = Router::new()
            .route("/new", post(FschedService::new_handler))
            .route("/count", post(FschedService::count_handler))
            .with_state(fsched_svc);

        let sysfo_svc = SysfoService::new(sysfo);
        let exporter_app = Router::new()
            .route("/info", get(SysfoService::info_handler))
            .with_state(sysfo_svc);

        let app = Router::new()
            .nest("/task", task_app)
            .nest("/system", exporter_app);

        let listener = tokio::net::TcpListener::bind("localhost:3000").await.unwrap();
        axum::serve(listener, app).await.unwrap();
    }).await;

    fsched.daemon().await;
}

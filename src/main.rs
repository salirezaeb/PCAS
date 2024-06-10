mod sysfo;
mod fsched;

use axum::{
    routing::post,
    Router,
};
use tokio::time::Duration;

use fsched::runtime::Runtime;
use fsched::service::HTTPService;
use sysfo::runtime::Runtime as SysfoRuntime;

#[tokio::main]
async fn main() {
    let fsched = Runtime::new();

    let scrape_interval = Duration::from_secs(5);

    let mut sysfo = SysfoRuntime::new(scrape_interval);

    fsched.add_function(|| async move {
        sysfo.run().await;
    }).await;

    let runtime = fsched.clone();

    fsched.add_function(|| async move {
        let http_service = HTTPService::new(runtime);

        let app = Router::new()
            .route("/task/count", post(HTTPService::task_count))
            .route("/process/new", post(HTTPService::new_process))
            .with_state(http_service);

        let listener = tokio::net::TcpListener::bind("localhost:3000").await.unwrap();
        axum::serve(listener, app).await.unwrap();
    }).await;

    fsched.run().await;
}

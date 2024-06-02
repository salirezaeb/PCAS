mod sysfo;
mod fsched;

use tokio::time::Duration;

use fsched::process::Process;
use fsched::runtime::Runtime;
use sysfo::runtime::Runtime as SysfoRuntime;

#[tokio::main]
async fn main() {
    let fsched = Runtime::new();

    let scrape_interval = Duration::from_secs(15);

    let mut sysfo = SysfoRuntime::new(scrape_interval);

    fsched.add_function(|| async move {
        sysfo.run().await;
    }).await;

    let commands = vec![
        "sleep 5".to_string(),
        "echo hello, world!".to_string(),
        "ls -lah".to_string(),
        "sleep 1 && echo pagh".to_string(),
    ];

    for command in commands {
        let proc = Process::new(command);

        fsched.add_process(proc).await;
    }

    fsched.run().await;
}

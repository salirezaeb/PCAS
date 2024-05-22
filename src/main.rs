mod sysfo;
mod fsched;

use tokio::io::{self};
use tokio::time::Duration;

#[tokio::main]
async fn main() -> io::Result<()> {
    let scrape_interval = Duration::from_secs(15);

    let mut tasks = vec![];

    let commands = vec![
        "sleep 5".to_string(),
        "echo hello, world!".to_string(),
        "ls -lah".to_string(),
        "sleep 1 && echo pagh".to_string(),
    ];

    sysfo::launch_exporter(scrape_interval, &mut tasks);
    fsched::launch_tasks(commands, &mut tasks);

    for task in tasks {
        if let Err(e) = task.await {
            eprintln!("Error executing task: {:?}", e);
        }
    }

    Ok(())
}


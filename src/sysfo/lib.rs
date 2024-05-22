use sysinfo::System;
use serde::{Serialize, Deserialize};
use tokio::task::JoinHandle;
use tokio::time::{self, Duration};

#[derive(Debug, Deserialize, Serialize)]
pub struct SystemInfo {
    cpu_cores: usize,
    free_ram: u64,
    total_ram: u64,
    used_ram: u64,
    free_swap: u64,
    total_swap: u64,
    used_swap: u64,
}

pub fn collect_system_info() -> SystemInfo {
    let mut sys = System::new_all();

    sys.refresh_all();

    let cpu_cores = sys.cpus().len();

    let free_ram = sys.available_memory();
    let total_ram = sys.total_memory();
    let used_ram = total_ram - free_ram;

    let free_swap = sys.free_swap();
    let total_swap = sys.total_swap();
    let used_swap = total_swap - free_swap;

    SystemInfo {
        cpu_cores,
        free_ram,
        total_ram,
        used_ram, free_swap,
        total_swap,
        used_swap,
    }
}

pub async fn export_system_info(interval: Duration) {
    let mut interval_timer = time::interval(interval);

    loop {
        interval_timer.tick().await;

        let info = collect_system_info();

        println!("{:#?}", info);
    }
}

pub fn launch_exporter(interval: Duration, tasks: &mut Vec<JoinHandle<()>>) {
    let task = tokio::spawn(async move {
        export_system_info(interval).await;
    });

    tasks.push(task);
}


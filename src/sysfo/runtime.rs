use sysinfo::System;
use serde::{Serialize, Deserialize};
use tokio::time::{self, Duration, Interval};

#[derive(Debug, Deserialize, Serialize)]
pub struct SystemInfo {
    cpu_cores: usize,
    free_ram: u64,
    total_ram: u64,
    used_ram: u64, free_swap: u64,
    total_swap: u64,
    used_swap: u64,
}

impl Default for SystemInfo {
    fn default() -> Self {
        SystemInfo {
            cpu_cores: 0,
            free_ram: 0,
            total_ram: 0,
            used_ram: 0,
            free_swap: 0,
            total_swap: 0,
            used_swap: 0,
        }
    }
}

pub struct Runtime {
    system: sysinfo::System,
    interval: Interval,
    info: SystemInfo,
}

impl Runtime {
    pub fn new(interval: Duration) -> Runtime {
        let system = System::new_all();

        Runtime {
            system,
            interval: time::interval(interval),
            info: SystemInfo::default(),
        }
    }

    pub fn collect_info(&mut self) {
        self.system.refresh_all();

        let cpu_cores = self.system.cpus().len();

        let free_ram = self.system.available_memory();
        let total_ram = self.system.total_memory();
        let used_ram = total_ram - free_ram;

        let free_swap = self.system.free_swap();
        let total_swap = self.system.total_swap();
        let used_swap = total_swap - free_swap;

        self.info = SystemInfo {
            cpu_cores,
            free_ram,
            total_ram,
            used_ram,
            free_swap,
            total_swap,
            used_swap,
        };
    }

    pub async fn run(&mut self) {
        loop {
            self.interval.tick().await;

            self.collect_info();

            println!("{:#?}", self.info);
        }
    }
}


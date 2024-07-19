use std::sync::Arc;

use serde::{Serialize, Deserialize};
use sysinfo::System;
use tokio::sync::Mutex;

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SystemInfo {
    cpu_cores: usize,
    free_ram: u64,
    total_ram: u64,
    used_ram: u64, 
    free_swap: u64,
    total_swap: u64,
    used_swap: u64,
    free_cache: u64,
    total_cache: u64,
    used_cache: u64,
}

#[derive(Clone)]
pub struct Runtime {
    system: Arc<Mutex<sysinfo::System>>,
    dummy_cache_bundle: (u64, u64),
}

impl Runtime {
    // FIXME: some dummy data read from config file will do for now
    pub fn new(dummy_cache_bundle: (u64, u64)) -> Runtime {
        Runtime {
            system: Arc::new(Mutex::new(System::new_all())),
            dummy_cache_bundle,
        }
    }

    pub async fn export_info(&mut self) -> SystemInfo {
        let mut system = self.system.lock().await;

        system.refresh_all();

        let cpu_cores = system.cpus().len();

        let free_ram = system.available_memory();
        let total_ram = system.total_memory();
        let used_ram = total_ram - free_ram;

        let free_swap = system.free_swap();
        let total_swap = system.total_swap();
        let used_swap = total_swap - free_swap;

        let (free_cache, total_cache) = self.dummy_cache_bundle;
        let used_cache = total_cache - free_cache;

        SystemInfo {
            cpu_cores,
            free_ram,
            total_ram,
            used_ram,
            free_swap,
            total_swap,
            used_swap,
            free_cache,
            total_cache,
            used_cache,
        }
    }
}


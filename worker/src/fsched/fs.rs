use std::io::{self, Error, ErrorKind};
use std::env;
use std::path::PathBuf;

use tokio::io::AsyncWriteExt;
use tokio::fs::File;

const ROOT_DIRECTORY: &str = "fsched-uploads";

pub struct FilesystemHandle {
    temp_dir: PathBuf,
}

impl FilesystemHandle {
    pub fn new() -> io::Result<Self> {
        let temp_dir = env::temp_dir().join(ROOT_DIRECTORY);
        std::fs::create_dir_all(&temp_dir)?;

        Ok(FilesystemHandle { temp_dir })
    }

    pub async fn create_file(&self, filename: String, content: &[u8]) -> Result<(), io::Error> {
        let file_path = self.temp_dir.join(filename);
        let mut file = File::create(&file_path).await?;
        file.write_all(content).await?;

        Ok(())
    }

    pub fn get_filepath(&self, filename: String) -> Result<String, Error> {
        match self.temp_dir.join(filename).to_str() {
            Some(filepath) => Ok(String::from(filepath)),
            _ => Err(Error::new(ErrorKind::Other, "No such file exists")),
        }
    }
}


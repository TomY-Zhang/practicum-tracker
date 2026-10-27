// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use std::sync::Mutex;
use std::time::Duration;
use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tokio::time::sleep;

use anyhow::Result;
use anyhow::bail;

const DB_ENV_VAR: &str = "PRACTICUM_TRACKER_DB";

struct SidecarProcess(Mutex<Option<CommandChild>>);

fn main() -> Result<()> {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let main_window = app
                .get_webview_window("main")
                .expect("Failed to get main window");

            let db_path = get_database_path()?;
            let sidecar = app
                .shell()
                .sidecar("tracker")?
                .set_process_group(true)
                .env(DB_ENV_VAR, db_path);
            let (mut events, child) = sidecar.spawn()?;
            app.manage(SidecarProcess(Mutex::new(Some(child))));

            tauri::async_runtime::spawn(async move {
                while let Some(event) = events.recv().await {
                    match event {
                        CommandEvent::Stderr(line) => {
                            eprintln!("tracker stderr: {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Error(error) => eprintln!("tracker error: {error}"),
                        CommandEvent::Terminated(status) => {
                            eprintln!("tracker exited: {:?}", status);
                        }
                        _ => {}
                    }
                }
            });

            tauri::async_runtime::spawn(async move {
                // TODO: add loading screen while the sidecar is starting up
                sleep(Duration::from_secs(2)).await;
                main_window
                    .eval("window.location.replace('http://localhost:8501');")
                    .expect("Failed to load the URL in the main window");
            });
            Ok(())
        })
        .on_window_event(|window, event| {
            if matches!(event, tauri::WindowEvent::CloseRequested { .. }) {
                let state = window.state::<SidecarProcess>();
                let child = state.0.lock().unwrap().take();
                if let Some(child) = child
                    && let Err(error) = child.kill()
                {
                    eprintln!("failed to stop tracker sidecar: {error}");
                }
            }
        })
        .run(tauri::generate_context!())?;
    Ok(())
}

fn get_database_path() -> Result<String> {
    if let Ok(db_path) = env::var(DB_ENV_VAR) {
        return Ok(db_path);
    }
    if let Some(db_path) = option_env!("PRACTICUM_TRACKER_DB") {
        return Ok(db_path.to_owned());
    }
    let path = match env::consts::OS {
        "windows" => {
            let local_app_data = env::var("LOCALAPPDATA").unwrap();
            format!("{}/practicum-tracker/tracker.db", local_app_data)
        }
        "linux" => {
            let home_dir = env::var("HOME").unwrap();
            format!("{}/.config/practicum-tracker/tracker.db", home_dir)
        }
        _ => bail!("Unsupported operating system: {}", env::consts::OS),
    };
    Ok(path)
}

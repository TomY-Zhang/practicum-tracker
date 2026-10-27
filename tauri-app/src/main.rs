// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use std::time::Duration;
use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use tokio::time::sleep;

// TODO: add a way to gracefully shutdown the sidecar when the main window is closed
// TODO: inject environment variables into the sidecar process

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let main_window = app.get_webview_window("main").unwrap();
            let sidecar = app.shell().sidecar("tracker").unwrap();

            tauri::async_runtime::spawn(async move {
                let (mut _rx, mut _child) = sidecar.spawn().expect("Failed to spawn sidecar");

                // wait for the streamlit server to start
                sleep(Duration::from_secs(2)).await;
                main_window
                    .eval("window.location.replace('http://localhost:8501');")
                    .expect("Failed to load the URL in the main window");
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

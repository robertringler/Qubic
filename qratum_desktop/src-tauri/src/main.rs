#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, SystemTray, SystemTrayMenu, Manager};
use std::sync::{Arc, Mutex};

mod backend;
mod commands;
mod tray;

// Lightweight in-memory database (no SQLite)
#[derive(Default)]
pub struct AppState {
    logs: Arc<Mutex<Vec<backend::LogEntry>>>,
}

fn main() {
    // System tray setup
    let tray_menu = SystemTrayMenu::new()
        .add_item(CustomMenuItem::new("show".to_string(), "Show"))
        .add_item(CustomMenuItem::new("hide".to_string(), "Hide"))
        .add_native_item(tauri::SystemTrayMenuItem::Separator)
        .add_item(CustomMenuItem::new("quit".to_string(), "Quit"));
    
    let tray = SystemTray::new().with_menu(tray_menu);
    
    let app = tauri::Builder::<tauri::Wry>::default()
        .manage(AppState::default())
        .system_tray(tray)
        .on_system_tray_event(tray::handle_tray_event)
        .invoke_handler(tauri::generate_handler![
            commands::get_health,
            commands::execute_kernel,
            commands::get_logs,
        ])
        .build(tauri::generate_context!())
        .expect("error while building tauri application");
    
    app.run(|_app_handle, event| match event {
        tauri::RunEvent::ExitRequested { api, .. } => {
            api.prevent_exit();
        }
        _ => {}
    });
}

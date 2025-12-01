//! NetBoozt Tauri Backend
//! 
//! Backend Rust para NetBoozt v3.0
//! Maneja todas las operaciones de red y sistema.
//!
//! By LOUST (www.loust.pro)

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

mod commands;

use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu,
    SystemTrayMenuItem, WindowEvent,
};

fn create_system_tray() -> SystemTray {
    let show = CustomMenuItem::new("show".to_string(), "Mostrar NetBoozt");
    let dns_cloudflare = CustomMenuItem::new("dns_cloudflare".to_string(), "DNS: Cloudflare");
    let dns_google = CustomMenuItem::new("dns_google".to_string(), "DNS: Google");
    let dns_auto = CustomMenuItem::new("dns_auto".to_string(), "DNS: Auto (Mejor)");
    let diagnose = CustomMenuItem::new("diagnose".to_string(), "Diagnóstico rápido");
    let quit = CustomMenuItem::new("quit".to_string(), "Salir");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(dns_cloudflare)
        .add_item(dns_google)
        .add_item(dns_auto)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(diagnose)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

fn handle_system_tray_event(app: &tauri::AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::LeftClick { .. } => {
            // Mostrar ventana al hacer click izquierdo
            if let Some(window) = app.get_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }
        SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
            "show" => {
                if let Some(window) = app.get_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "dns_cloudflare" => {
                // TODO: Cambiar DNS a Cloudflare
                println!("Changing DNS to Cloudflare");
            }
            "dns_google" => {
                // TODO: Cambiar DNS a Google
                println!("Changing DNS to Google");
            }
            "dns_auto" => {
                // TODO: Usar mejor DNS automáticamente
                println!("Using best DNS");
            }
            "diagnose" => {
                // TODO: Ejecutar diagnóstico rápido
                println!("Running quick diagnostic");
            }
            "quit" => {
                std::process::exit(0);
            }
            _ => {}
        },
        _ => {}
    }
}

fn main() {
    env_logger::init();

    tauri::Builder::default()
        .system_tray(create_system_tray())
        .on_system_tray_event(handle_system_tray_event)
        .on_window_event(|event| {
            // Minimizar a tray en vez de cerrar
            if let WindowEvent::CloseRequested { api, .. } = event.event() {
                event.window().hide().unwrap();
                api.prevent_close();
            }
        })
        .invoke_handler(tauri::generate_handler![
            commands::network::get_network_adapters,
            commands::network::get_current_dns,
            commands::network::set_dns_servers,
            commands::network::reset_dns_to_dhcp,
            commands::network::flush_dns_cache,
            commands::diagnostics::run_full_diagnostic,
            commands::diagnostics::quick_check,
            commands::optimizer::get_current_settings,
            commands::optimizer::apply_profile,
            commands::optimizer::reset_to_defaults,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

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

// Módulos
mod commands;
mod services;
mod tray;

use tauri::{Manager, WindowEvent};

fn main() {
    // Inicializar logger
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info"))
        .format_timestamp_millis()
        .init();

    log::info!("🚀 Iniciando NetBoozt v3.0...");

    tauri::Builder::default()
        // System Tray
        .system_tray(tray::create_system_tray())
        .on_system_tray_event(tray::handle_system_tray_event)
        
        // Eventos de ventana
        .on_window_event(|event| {
            // Minimizar a tray en vez de cerrar
            if let WindowEvent::CloseRequested { api, .. } = event.event() {
                log::info!("Ventana cerrada, minimizando a tray...");
                let _ = event.window().hide();
                api.prevent_close();
            }
        })
        
        // Setup inicial
        .setup(|app| {
            log::info!("Configurando aplicación...");
            
            // Obtener ventana principal
            let window = app.get_window("main").expect("No se encontró ventana principal");
            
            // En desarrollo, mostrar devtools
            #[cfg(debug_assertions)]
            {
                window.open_devtools();
            }
            
            // Centrar ventana
            let _ = window.center();
            
            log::info!("✅ NetBoozt inicializado correctamente");
            Ok(())
        })
        
        // Comandos Tauri
        .invoke_handler(tauri::generate_handler![
            // Network commands
            commands::network::get_network_adapters,
            commands::network::get_current_dns,
            commands::network::set_dns_servers,
            commands::network::reset_dns_to_dhcp,
            commands::network::flush_dns_cache,
            
            // Diagnostics commands
            commands::diagnostics::run_full_diagnostic,
            commands::diagnostics::quick_check,
            commands::diagnostics::ping_host,
            commands::diagnostics::check_dns_health,
            commands::diagnostics::check_single_dns_health,
            
            // Optimizer commands
            commands::optimizer::get_current_settings,
            commands::optimizer::apply_profile,
            commands::optimizer::reset_to_defaults,
            commands::optimizer::get_available_optimizations,
            
            // Monitoring commands
            commands::monitoring::start_monitoring,
            commands::monitoring::stop_monitoring,
            commands::monitoring::get_current_metrics,
            
            // Speed test commands
            commands::speedtest::run_speed_test,
            commands::speedtest::get_last_speedtest,
            
            // Utility commands
            is_admin,
            get_app_version,
            open_url,
        ])
        
        .run(tauri::generate_context!())
        .expect("Error al iniciar NetBoozt");
}

// ============================================
// Utility Commands
// ============================================

/// Verificar si se ejecuta como administrador
#[tauri::command]
fn is_admin() -> bool {
    #[cfg(windows)]
    {
        use std::process::Command;
        
        let output = Command::new("powershell")
            .args([
                "-NoProfile",
                "-Command",
                "([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"
            ])
            .output();
        
        match output {
            Ok(o) => String::from_utf8_lossy(&o.stdout).trim() == "True",
            Err(_) => false,
        }
    }
    
    #[cfg(not(windows))]
    {
        false
    }
}

/// Obtener versión de la aplicación
#[tauri::command]
fn get_app_version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}

/// Abrir URL en navegador
#[tauri::command]
async fn open_url(url: String) -> Result<(), String> {
    #[cfg(windows)]
    {
        use std::process::Command;
        Command::new("cmd")
            .args(["/c", "start", "", &url])
            .spawn()
            .map_err(|e| format!("Error abriendo URL: {}", e))?;
    }
    
    #[cfg(not(windows))]
    {
        use std::process::Command;
        Command::new("xdg-open")
            .arg(&url)
            .spawn()
            .map_err(|e| format!("Error abriendo URL: {}", e))?;
    }
    
    Ok(())
}

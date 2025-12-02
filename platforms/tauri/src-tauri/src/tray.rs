//! System Tray Module
//!
//! Manejo completo del System Tray con menú y acciones.
//!
//! By LOUST (www.loust.pro)

use tauri::{
    AppHandle, CustomMenuItem, Manager, SystemTray, SystemTrayEvent, 
    SystemTrayMenu, SystemTrayMenuItem, SystemTraySubmenu,
};

use crate::services::{diagnostics, dns, notifications};

/// Crear el menú del System Tray
pub fn create_system_tray() -> SystemTray {
    // Items principales
    let show = CustomMenuItem::new("show", "🚀 Mostrar NetBoozt");
    let hide = CustomMenuItem::new("hide", "👁️ Ocultar");
    
    // Submenú DNS
    let dns_cloudflare = CustomMenuItem::new("dns_cloudflare", "☁️ Cloudflare (1.1.1.1)");
    let dns_google = CustomMenuItem::new("dns_google", "🔵 Google (8.8.8.8)");
    let dns_quad9 = CustomMenuItem::new("dns_quad9", "🛡️ Quad9 (9.9.9.9)");
    let dns_opendns = CustomMenuItem::new("dns_opendns", "🔶 OpenDNS");
    let dns_adguard = CustomMenuItem::new("dns_adguard", "🚫 AdGuard (Ad-block)");
    let dns_auto = CustomMenuItem::new("dns_auto", "⚡ Auto (Mejor)");
    let dns_reset = CustomMenuItem::new("dns_reset", "🔄 DHCP (Por defecto)");
    let dns_flush = CustomMenuItem::new("dns_flush", "🧹 Limpiar Caché DNS");
    
    let dns_submenu = SystemTraySubmenu::new(
        "🌐 DNS",
        SystemTrayMenu::new()
            .add_item(dns_auto)
            .add_native_item(SystemTrayMenuItem::Separator)
            .add_item(dns_cloudflare)
            .add_item(dns_google)
            .add_item(dns_quad9)
            .add_item(dns_opendns)
            .add_item(dns_adguard)
            .add_native_item(SystemTrayMenuItem::Separator)
            .add_item(dns_reset)
            .add_item(dns_flush),
    );
    
    // Submenú Optimizaciones
    let opt_conservative = CustomMenuItem::new("opt_conservative", "🟢 Conservador");
    let opt_balanced = CustomMenuItem::new("opt_balanced", "🟡 Balanceado (Recomendado)");
    let opt_aggressive = CustomMenuItem::new("opt_aggressive", "🔴 Agresivo");
    let opt_reset = CustomMenuItem::new("opt_reset", "↩️ Restaurar Defectos");
    
    let opt_submenu = SystemTraySubmenu::new(
        "⚡ Optimizaciones",
        SystemTrayMenu::new()
            .add_item(opt_conservative)
            .add_item(opt_balanced)
            .add_item(opt_aggressive)
            .add_native_item(SystemTrayMenuItem::Separator)
            .add_item(opt_reset),
    );
    
    // Diagnósticos
    let diagnose_quick = CustomMenuItem::new("diagnose_quick", "🔍 Check Rápido");
    let diagnose_full = CustomMenuItem::new("diagnose_full", "🔬 Diagnóstico Completo");
    
    // Otros
    let about = CustomMenuItem::new("about", "ℹ️ Acerca de");
    let quit = CustomMenuItem::new("quit", "❌ Salir");

    // Construir menú principal
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_submenu(dns_submenu)
        .add_submenu(opt_submenu)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(diagnose_quick)
        .add_item(diagnose_full)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(about)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

/// Manejar eventos del System Tray
pub fn handle_system_tray_event(app: &AppHandle, event: SystemTrayEvent) {
    match event {
        // Click izquierdo - Mostrar ventana
        SystemTrayEvent::LeftClick { .. } => {
            show_main_window(app);
        }
        
        // Click en items del menú
        SystemTrayEvent::MenuItemClick { id, .. } => {
            handle_menu_click(app, &id);
        }
        
        _ => {}
    }
}

/// Manejar clicks en items del menú
fn handle_menu_click(app: &AppHandle, id: &str) {
    match id {
        // Ventana
        "show" => show_main_window(app),
        "hide" => hide_main_window(app),
        
        // DNS
        "dns_cloudflare" => change_dns(app, "cloudflare"),
        "dns_google" => change_dns(app, "google"),
        "dns_quad9" => change_dns(app, "quad9"),
        "dns_opendns" => change_dns(app, "opendns"),
        "dns_adguard" => change_dns(app, "adguard"),
        "dns_auto" => select_best_dns(app),
        "dns_reset" => reset_dns(app),
        "dns_flush" => flush_dns(app),
        
        // Optimizaciones
        "opt_conservative" => apply_optimization(app, "Conservative"),
        "opt_balanced" => apply_optimization(app, "Balanced"),
        "opt_aggressive" => apply_optimization(app, "Aggressive"),
        "opt_reset" => reset_optimizations(app),
        
        // Diagnósticos
        "diagnose_quick" => run_quick_diagnostic(app),
        "diagnose_full" => run_full_diagnostic(app),
        
        // Otros
        "about" => show_about(app),
        "quit" => quit_app(),
        
        _ => {}
    }
}

// ============================================
// Acciones de Ventana
// ============================================

fn show_main_window(app: &AppHandle) {
    if let Some(window) = app.get_window("main") {
        let _ = window.show();
        let _ = window.unminimize();
        let _ = window.set_focus();
    }
}

fn hide_main_window(app: &AppHandle) {
    if let Some(window) = app.get_window("main") {
        let _ = window.hide();
    }
}

// ============================================
// Acciones DNS
// ============================================

fn change_dns(app: &AppHandle, provider_id: &str) {
    log::info!("Cambiando DNS a: {}", provider_id);
    
    match dns::set_dns_by_provider(provider_id) {
        Ok(true) => {
            let provider = dns::get_provider(provider_id)
                .map(|p| p.name)
                .unwrap_or(provider_id);
            
            log::info!("DNS cambiado exitosamente a {}", provider);
            let _ = notifications::notify_dns_changed(app, provider);
            
            // Emitir evento al frontend
            let _ = app.emit_all("dns_changed", provider_id);
        }
        Ok(false) | Err(_) => {
            log::error!("Error cambiando DNS a {}", provider_id);
            let _ = notifications::notify_connection_error(app, "Error al cambiar DNS");
        }
    }
}

fn select_best_dns(app: &AppHandle) {
    log::info!("Seleccionando mejor DNS automáticamente...");
    
    // Ejecutar en thread para no bloquear
    let app_handle = app.clone();
    std::thread::spawn(move || {
        match dns::select_best_dns() {
            Ok(provider) => {
                log::info!("Mejor DNS encontrado: {} ({:.1}ms)", provider.name, 0.0);
                
                // Aplicar el DNS
                if let Err(e) = dns::set_dns_by_provider(provider.id) {
                    log::error!("Error aplicando DNS: {}", e);
                    return;
                }
                
                let _ = notifications::notify_dns_changed(&app_handle, provider.name);
                let _ = app_handle.emit_all("dns_changed", provider.id);
            }
            Err(e) => {
                log::error!("Error seleccionando mejor DNS: {}", e);
                let _ = notifications::notify_connection_error(&app_handle, &e);
            }
        }
    });
}

fn reset_dns(app: &AppHandle) {
    log::info!("Reseteando DNS a DHCP...");
    
    match dns::get_primary_adapter() {
        Ok(adapter) => {
            match dns::reset_dns_to_dhcp(&adapter) {
                Ok(true) => {
                    log::info!("DNS reseteado a DHCP");
                    let _ = notifications::notify_dns_changed(app, "DHCP (Automático)");
                    let _ = app.emit_all("dns_changed", "dhcp");
                }
                _ => {
                    log::error!("Error reseteando DNS");
                }
            }
        }
        Err(e) => log::error!("Error obteniendo adaptador: {}", e),
    }
}

fn flush_dns(app: &AppHandle) {
    log::info!("Limpiando caché DNS...");
    
    match dns::flush_dns_cache() {
        Ok(true) => {
            log::info!("Caché DNS limpiada");
            let _ = notifications::show_notification(
                app, 
                "NetBoozt", 
                "Caché DNS limpiada correctamente"
            );
        }
        _ => {
            log::error!("Error limpiando caché DNS");
        }
    }
}

// ============================================
// Acciones de Optimización
// ============================================

fn apply_optimization(app: &AppHandle, profile: &str) {
    log::info!("Aplicando perfil de optimización: {}", profile);
    
    let app_handle = app.clone();
    let profile_owned = profile.to_string();
    
    std::thread::spawn(move || {
        // Importar y ejecutar la optimización
        match crate::commands::optimizer::apply_profile_internal(&profile_owned) {
            Ok(applied) => {
                log::info!("Perfil {} aplicado: {} optimizaciones", profile_owned, applied.len());
                let _ = notifications::notify_optimization_applied(&app_handle, &profile_owned, applied.len());
                let _ = app_handle.emit_all("optimization_applied", &applied);
            }
            Err(e) => {
                log::error!("Error aplicando perfil: {}", e);
            }
        }
    });
}

fn reset_optimizations(app: &AppHandle) {
    log::info!("Restaurando optimizaciones por defecto...");
    
    let app_handle = app.clone();
    
    std::thread::spawn(move || {
        match crate::commands::optimizer::reset_to_defaults_internal() {
            Ok(reset) => {
                log::info!("Configuración restaurada: {} cambios", reset.len());
                let _ = notifications::show_notification(
                    &app_handle,
                    "NetBoozt",
                    &format!("Configuración restaurada ({} cambios)", reset.len())
                );
            }
            Err(e) => {
                log::error!("Error restaurando configuración: {}", e);
            }
        }
    });
}

// ============================================
// Acciones de Diagnóstico
// ============================================

fn run_quick_diagnostic(app: &AppHandle) {
    log::info!("Ejecutando diagnóstico rápido...");
    
    let result = diagnostics::quick_check();
    
    let emoji = if result.connected { "✅" } else { "❌" };
    let _ = notifications::show_notification(
        app,
        "NetBoozt - Quick Check",
        &format!("{} {}", emoji, result.message)
    );
    
    let _ = app.emit_all("quick_check_result", &result);
}

fn run_full_diagnostic(app: &AppHandle) {
    log::info!("Ejecutando diagnóstico completo...");
    
    let app_handle = app.clone();
    
    std::thread::spawn(move || {
        let result = diagnostics::run_full_diagnostic();
        
        let _ = notifications::notify_diagnostic_complete(&app_handle, &result.health.to_string());
        let _ = app_handle.emit_all("diagnostic_result", &result);
    });
}

// ============================================
// Otras Acciones
// ============================================

fn show_about(app: &AppHandle) {
    let _ = notifications::show_notification(
        app,
        "NetBoozt v3.0.0",
        "Network Optimization Tool for Windows\nBy LOUST (www.loust.pro)"
    );
}

fn quit_app() {
    log::info!("Saliendo de NetBoozt...");
    std::process::exit(0);
}

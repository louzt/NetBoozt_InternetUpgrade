//! Network commands module
//!
//! Comandos Tauri para operaciones de red.

use serde::{Deserialize, Serialize};
use std::process::Command;

#[cfg(windows)]
use std::os::windows::process::CommandExt;

/// Struct para deserializar desde PowerShell (campos PascalCase)
#[derive(Debug, Deserialize)]
struct PowerShellAdapter {
    #[serde(rename = "Name")]
    name: String,
    #[serde(rename = "InterfaceDescription")]
    description: String,
    #[serde(rename = "Status")]
    status: String,
    #[serde(rename = "LinkSpeed")]
    link_speed: String,
    #[serde(rename = "MacAddress")]
    mac_address: String,
}

/// Struct para serializar hacia el frontend (campos snake_case)
#[derive(Debug, Serialize)]
pub struct NetworkAdapter {
    pub name: String,
    pub description: String,
    pub status: String,
    pub link_speed: String,
    pub mac_address: String,
}

impl From<PowerShellAdapter> for NetworkAdapter {
    fn from(ps: PowerShellAdapter) -> Self {
        NetworkAdapter {
            name: ps.name,
            description: ps.description,
            status: ps.status,
            link_speed: ps.link_speed,
            mac_address: ps.mac_address,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DnsConfig {
    pub adapter: String,
    pub servers: Vec<String>,
    pub is_dhcp: bool,
}

/// Obtiene lista de adaptadores de red activos
#[tauri::command]
pub async fn get_network_adapters() -> Result<Vec<NetworkAdapter>, String> {
    let output = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            r#"Get-NetAdapter | Where-Object Status -eq 'Up' | 
               Select-Object Name, InterfaceDescription, Status, LinkSpeed, MacAddress | 
               ConvertTo-Json"#,
        ])
        .output()
        .map_err(|e| e.to_string())?;

    if !output.status.success() {
        return Err("Failed to get network adapters".to_string());
    }

    let json = String::from_utf8_lossy(&output.stdout);
    
    // Handle single adapter (returns object) vs multiple (returns array)
    let ps_adapters: Vec<PowerShellAdapter> = if json.trim().starts_with('[') {
        serde_json::from_str(&json).map_err(|e| format!("JSON array parse error: {}", e))?
    } else if json.trim().starts_with('{') {
        let adapter: PowerShellAdapter = serde_json::from_str(&json)
            .map_err(|e| format!("JSON object parse error: {}", e))?;
        vec![adapter]
    } else {
        return Ok(vec![]);
    };
    
    // Convert PowerShell structs to frontend structs
    Ok(ps_adapters.into_iter().map(NetworkAdapter::from).collect())
}

/// Obtiene configuración DNS actual
#[tauri::command]
pub async fn get_current_dns(adapter: String) -> Result<DnsConfig, String> {
    let command = format!(
        r#"Get-DnsClientServerAddress -InterfaceAlias '{}' -AddressFamily IPv4 | 
           Select-Object InterfaceAlias, ServerAddresses | ConvertTo-Json"#,
        adapter
    );

    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", &command])
        .creation_flags(0x08000000) // CREATE_NO_WINDOW
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    let json = String::from_utf8_lossy(&output.stdout).trim().to_string();
    
    // Si está vacío o es error, devolver configuración DHCP
    if json.is_empty() || json.starts_with("Get-DnsClientServerAddress") {
        log::warn!("No DNS config found for adapter '{}', assuming DHCP", adapter);
        return Ok(DnsConfig {
            adapter: adapter.clone(),
            servers: vec![],
            is_dhcp: true,
        });
    }
    
    #[derive(Deserialize)]
    struct PsResult {
        #[serde(rename = "InterfaceAlias")]
        interface_alias: Option<String>,
        #[serde(rename = "ServerAddresses")]
        server_addresses: Option<Vec<String>>,
    }

    match serde_json::from_str::<PsResult>(&json) {
        Ok(result) => {
            let servers = result.server_addresses.unwrap_or_default();
            Ok(DnsConfig {
                adapter: result.interface_alias.unwrap_or(adapter),
                servers: servers.clone(),
                is_dhcp: servers.is_empty(),
            })
        }
        Err(e) => {
            log::error!("Failed to parse DNS JSON '{}': {}", json, e);
            // Devolver DHCP como fallback
            Ok(DnsConfig {
                adapter,
                servers: vec![],
                is_dhcp: true,
            })
        }
    }
}

/// Establece servidores DNS (requiere ejecutar como admin)
#[tauri::command]
pub async fn set_dns_servers(
    adapter: String,
    primary: String,
    secondary: Option<String>,
) -> Result<bool, String> {
    // PowerShell requiere formato de array: @('ip1','ip2') o 'ip1','ip2'
    let dns_list = match secondary {
        Some(sec) => format!("'{}','{}'", primary, sec),
        None => format!("'{}'", primary),
    };

    let command = format!(
        "Set-DnsClientServerAddress -InterfaceAlias '{}' -ServerAddresses {}",
        adapter, dns_list
    );

    log::info!("Setting DNS: {}", command);

    // Intentar primero sin elevación
    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", &command])
        .creation_flags(0x08000000) // CREATE_NO_WINDOW
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if output.status.success() {
        log::info!("DNS set successfully to {} on {}", dns_list, adapter);
        return Ok(true);
    }
    
    let stderr = String::from_utf8_lossy(&output.stderr);
    
    // Si falla por permisos, intentar con elevación usando Start-Process
    if stderr.contains("PermissionDenied") || stderr.contains("Access") || stderr.contains("CIM") {
        log::warn!("DNS change requires elevation, attempting with admin privileges...");
        
        // Usar Start-Process -Verb RunAs para solicitar elevación
        let elevated_command = format!(
            "Start-Process powershell -ArgumentList '-NoProfile','-Command',\"Set-DnsClientServerAddress -InterfaceAlias '{}' -ServerAddresses {}\" -Verb RunAs -Wait",
            adapter.replace("'", "''"), dns_list
        );
        
        let elevated_output = Command::new("powershell")
            .args(["-NoProfile", "-Command", &elevated_command])
            .creation_flags(0x08000000) // CREATE_NO_WINDOW
            .output()
            .map_err(|e| format!("Failed to execute elevated PowerShell: {}", e))?;
        
        if elevated_output.status.success() {
            log::info!("DNS set successfully with elevation");
            return Ok(true);
        } else {
            let elevated_stderr = String::from_utf8_lossy(&elevated_output.stderr);
            log::error!("Elevated DNS set failed: {}", elevated_stderr);
            return Err("Se requieren permisos de administrador. Ejecuta NetBoozt como administrador o acepta el prompt de UAC.".to_string());
        }
    }

    log::error!("DNS set failed: {}", stderr);
    Err(format!("Error al configurar DNS: {}", stderr))
}

/// Resetea DNS a DHCP (requiere ejecutar como admin)
#[tauri::command]
pub async fn reset_dns_to_dhcp(adapter: String) -> Result<bool, String> {
    let command = format!(
        "Set-DnsClientServerAddress -InterfaceAlias '{}' -ResetServerAddresses",
        adapter
    );

    log::info!("Resetting DNS to DHCP: {}", command);

    // Intentar primero sin elevación
    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", &command])
        .creation_flags(0x08000000)
        .output()
        .map_err(|e| format!("Failed to execute PowerShell: {}", e))?;

    if output.status.success() {
        log::info!("DNS reset to DHCP successfully on {}", adapter);
        return Ok(true);
    }
    
    let stderr = String::from_utf8_lossy(&output.stderr);
    
    // Si falla por permisos, intentar con elevación
    if stderr.contains("PermissionDenied") || stderr.contains("Access") || stderr.contains("CIM") {
        log::warn!("DNS reset requires elevation, attempting with admin privileges...");
        
        let elevated_command = format!(
            "Start-Process powershell -ArgumentList '-NoProfile','-Command',\"Set-DnsClientServerAddress -InterfaceAlias '{}' -ResetServerAddresses\" -Verb RunAs -Wait",
            adapter.replace("'", "''")
        );
        
        let elevated_output = Command::new("powershell")
            .args(["-NoProfile", "-Command", &elevated_command])
            .creation_flags(0x08000000)
            .output()
            .map_err(|e| format!("Failed to execute elevated PowerShell: {}", e))?;
        
        if elevated_output.status.success() {
            log::info!("DNS reset to DHCP successfully with elevation");
            return Ok(true);
        } else {
            let elevated_stderr = String::from_utf8_lossy(&elevated_output.stderr);
            log::error!("Elevated DNS reset failed: {}", elevated_stderr);
            return Err("Se requieren permisos de administrador para resetear DNS.".to_string());
        }
    }

    log::error!("DNS reset failed: {}", stderr);
    Err(format!("Error al resetear DNS: {}", stderr))
}

/// Limpia cache DNS
#[tauri::command]
pub async fn flush_dns_cache() -> Result<bool, String> {
    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", "Clear-DnsClientCache"])
        .output()
        .map_err(|e| e.to_string())?;

    Ok(output.status.success())
}

// ==================== DNS INTELLIGENCE API ====================

use crate::services::{get_dns_intelligence, DnsMetrics, DnsIntelSummary, FailoverEvent, start_dns_intelligence, stop_dns_intelligence};

/// Obtener ranking completo de DNS con métricas
#[tauri::command]
pub async fn get_dns_ranking() -> Result<Vec<DnsMetrics>, String> {
    let intel = get_dns_intelligence();
    Ok(intel.get_all_metrics())
}

/// Obtener los mejores DNS
#[tauri::command]
pub async fn get_best_dns(count: Option<usize>) -> Result<Vec<DnsMetrics>, String> {
    let intel = get_dns_intelligence();
    Ok(intel.get_best_dns(count.unwrap_or(3)))
}

/// Obtener resumen del estado DNS Intelligence
#[tauri::command]
pub async fn get_dns_intel_summary() -> Result<DnsIntelSummary, String> {
    let intel = get_dns_intelligence();
    Ok(intel.get_summary())
}

/// Forzar check inmediato de todos los DNS
#[tauri::command]
pub async fn force_dns_check() -> Result<Vec<DnsMetrics>, String> {
    let intel = get_dns_intelligence();
    intel.force_check();
    Ok(intel.get_all_metrics())
}

/// Habilitar/deshabilitar auto-failover
#[tauri::command]
pub async fn set_dns_auto_failover(enabled: bool) -> Result<bool, String> {
    let intel = get_dns_intelligence();
    intel.set_auto_failover(enabled);
    Ok(intel.is_auto_failover_enabled())
}

/// Obtener historial de failovers DNS
#[tauri::command]
pub async fn get_dns_failover_history() -> Result<Vec<FailoverEvent>, String> {
    let intel = get_dns_intelligence();
    Ok(intel.get_failover_history())
}

/// Iniciar el servicio de DNS Intelligence
#[tauri::command]
pub async fn start_dns_intel_service() -> Result<String, String> {
    start_dns_intelligence();
    log::info!("🧠 DNS Intelligence service started via command");
    Ok("DNS Intelligence service started".to_string())
}

/// Detener el servicio de DNS Intelligence
#[tauri::command]
pub async fn stop_dns_intel_service() -> Result<String, String> {
    stop_dns_intelligence();
    log::info!("🧠 DNS Intelligence service stopped via command");
    Ok("DNS Intelligence service stopped".to_string())
}

/// Obtener el mejor DNS actual
#[tauri::command]
pub async fn get_current_best_dns() -> Result<Option<String>, String> {
    let intel = get_dns_intelligence();
    Ok(intel.get_current_best())
}

/// Aplicar el mejor DNS automáticamente
#[tauri::command]
pub async fn apply_best_dns(adapter: String) -> Result<bool, String> {
    let intel = get_dns_intelligence();
    
    // Obtener el mejor DNS
    let best = intel.get_best_dns(1);
    if best.is_empty() {
        return Err("No hay DNS saludables disponibles".to_string());
    }
    
    let best_dns = &best[0];
    log::info!("🏆 Applying best DNS: {} ({})", best_dns.name, best_dns.address);
    
    // Determinar DNS secundario (siguiente mejor del mismo proveedor o el #2)
    let secondary = if best.len() > 1 {
        Some(best[1].address.clone())
    } else {
        // Buscar secundario del mismo proveedor
        let all = intel.get_all_metrics();
        all.iter()
            .find(|m| m.name.contains(&best_dns.name.replace(" Secondary", "")) && m.address != best_dns.address)
            .map(|m| m.address.clone())
    };
    
    // Aplicar DNS
    let dns_list = match secondary {
        Some(sec) => format!("{},{}", best_dns.address, sec),
        None => best_dns.address.clone(),
    };
    
    let command = format!(
        "Set-DnsClientServerAddress -InterfaceAlias '{}' -ServerAddresses {}",
        adapter, dns_list
    );
    
    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", &command])
        .output()
        .map_err(|e| e.to_string())?;
    
    if output.status.success() {
        log::info!("✅ Best DNS applied successfully");
    }
    
    Ok(output.status.success())
}

/// Abrir el Administrador de Dispositivos de Windows
#[tauri::command]
pub async fn open_device_manager() -> Result<bool, String> {
    let output = Command::new("cmd")
        .args(["/C", "start", "devmgmt.msc"])
        .output()
        .map_err(|e| format!("Failed to open Device Manager: {}", e))?;
    
    if output.status.success() {
        log::info!("📱 Device Manager opened");
    }
    
    Ok(output.status.success())
}
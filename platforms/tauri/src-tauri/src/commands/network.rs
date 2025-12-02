//! Network commands module
//!
//! Comandos Tauri para operaciones de red.

use serde::{Deserialize, Serialize};
use std::process::Command;

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
        .output()
        .map_err(|e| e.to_string())?;

    let json = String::from_utf8_lossy(&output.stdout);
    
    #[derive(Deserialize)]
    struct PsResult {
        #[serde(rename = "InterfaceAlias")]
        interface_alias: String,
        #[serde(rename = "ServerAddresses")]
        server_addresses: Vec<String>,
    }

    let result: PsResult = serde_json::from_str(&json).map_err(|e| e.to_string())?;

    Ok(DnsConfig {
        adapter: result.interface_alias,
        servers: result.server_addresses.clone(),
        is_dhcp: result.server_addresses.is_empty(),
    })
}

/// Establece servidores DNS
#[tauri::command]
pub async fn set_dns_servers(
    adapter: String,
    primary: String,
    secondary: Option<String>,
) -> Result<bool, String> {
    let dns_list = match secondary {
        Some(sec) => format!("{},{}", primary, sec),
        None => primary,
    };

    let command = format!(
        "Set-DnsClientServerAddress -InterfaceAlias '{}' -ServerAddresses {}",
        adapter, dns_list
    );

    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", &command])
        .output()
        .map_err(|e| e.to_string())?;

    Ok(output.status.success())
}

/// Resetea DNS a DHCP
#[tauri::command]
pub async fn reset_dns_to_dhcp(adapter: String) -> Result<bool, String> {
    let command = format!(
        "Set-DnsClientServerAddress -InterfaceAlias '{}' -ResetServerAddresses",
        adapter
    );

    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", &command])
        .output()
        .map_err(|e| e.to_string())?;

    Ok(output.status.success())
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

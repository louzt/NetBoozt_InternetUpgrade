//! DNS Service Module
//!
//! Servicio de DNS centralizado para operaciones de red.
//! Usado por comandos y system tray.
//!
//! By LOUST (www.loust.pro)

use std::process::Command;

#[cfg(windows)]
use std::os::windows::process::CommandExt;

#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x08000000;

/// Proveedores DNS predefinidos
#[derive(Debug, Clone)]
pub struct DnsProvider {
    pub id: &'static str,
    pub name: &'static str,
    pub primary: &'static str,
    pub secondary: &'static str,
    #[allow(dead_code)]
    pub tier: u8,
}

/// Lista de proveedores DNS
pub const DNS_PROVIDERS: &[DnsProvider] = &[
    DnsProvider {
        id: "cloudflare",
        name: "Cloudflare",
        primary: "1.1.1.1",
        secondary: "1.0.0.1",
        tier: 1,
    },
    DnsProvider {
        id: "google",
        name: "Google",
        primary: "8.8.8.8",
        secondary: "8.8.4.4",
        tier: 2,
    },
    DnsProvider {
        id: "quad9",
        name: "Quad9",
        primary: "9.9.9.9",
        secondary: "149.112.112.112",
        tier: 3,
    },
    DnsProvider {
        id: "opendns",
        name: "OpenDNS",
        primary: "208.67.222.222",
        secondary: "208.67.220.220",
        tier: 4,
    },
    DnsProvider {
        id: "adguard",
        name: "AdGuard",
        primary: "94.140.14.14",
        secondary: "94.140.15.15",
        tier: 5,
    },
    DnsProvider {
        id: "cleanbrowsing",
        name: "CleanBrowsing",
        primary: "185.228.168.9",
        secondary: "185.228.169.9",
        tier: 6,
    },
];

/// Obtener proveedor DNS por ID
pub fn get_provider(id: &str) -> Option<&DnsProvider> {
    DNS_PROVIDERS.iter().find(|p| p.id == id)
}

/// Obtener adaptador de red principal (activo)
pub fn get_primary_adapter() -> Result<String, String> {
    let ps_script = r#"
        Get-NetAdapter | Where-Object Status -eq 'Up' | 
        Select-Object -First 1 -ExpandProperty Name
    "#;

    run_powershell(ps_script)
}

/// Cambiar DNS de un adaptador
pub fn set_dns(adapter: &str, primary: &str, secondary: Option<&str>) -> Result<bool, String> {
    let dns_list = match secondary {
        Some(sec) => format!("{},{}", primary, sec),
        None => primary.to_string(),
    };

    let command = format!(
        "Set-DnsClientServerAddress -InterfaceAlias '{}' -ServerAddresses {}",
        adapter, dns_list
    );

    let result = run_powershell(&command)?;
    Ok(result.is_empty() || !result.contains("error"))
}

/// Cambiar DNS por ID de proveedor
pub fn set_dns_by_provider(provider_id: &str) -> Result<bool, String> {
    let provider = get_provider(provider_id)
        .ok_or_else(|| format!("Proveedor DNS '{}' no encontrado", provider_id))?;

    let adapter = get_primary_adapter()?;
    
    set_dns(&adapter, provider.primary, Some(provider.secondary))
}

/// Resetear DNS a DHCP (automático)
pub fn reset_dns_to_dhcp(adapter: &str) -> Result<bool, String> {
    let command = format!(
        "Set-DnsClientServerAddress -InterfaceAlias '{}' -ResetServerAddresses",
        adapter
    );

    let result = run_powershell(&command)?;
    Ok(result.is_empty() || !result.contains("error"))
}

/// Limpiar caché DNS
pub fn flush_dns_cache() -> Result<bool, String> {
    let result = run_powershell("Clear-DnsClientCache")?;
    Ok(result.is_empty() || !result.contains("error"))
}

/// Seleccionar mejor DNS automáticamente basado en latencia
pub fn select_best_dns() -> Result<DnsProvider, String> {
    let mut best_provider: Option<&DnsProvider> = None;
    let mut best_latency = f64::MAX;

    for provider in DNS_PROVIDERS {
        if let Ok(latency) = ping_dns(provider.primary) {
            log::info!("DNS {} latency: {:.1}ms", provider.name, latency);
            if latency < best_latency && latency > 0.0 {
                best_latency = latency;
                best_provider = Some(provider);
            }
        }
    }

    best_provider
        .map(|p| p.clone())
        .ok_or_else(|| "No se pudo determinar el mejor DNS".to_string())
}

/// Verificar latencia de un servidor DNS
pub fn ping_dns(dns_server: &str) -> Result<f64, String> {
    let ps_script = format!(
        r#"
        $ping = Test-Connection -ComputerName {} -Count 1 -ErrorAction SilentlyContinue
        if ($ping) {{ $ping.ResponseTime }} else {{ -1 }}
        "#,
        dns_server
    );

    let result = run_powershell(&ps_script)?;
    result.trim().parse::<f64>()
        .map_err(|e| format!("Error parsing latency: {}", e))
}

/// Verificar si un DNS resuelve correctamente
#[allow(dead_code)]
pub fn check_dns_resolution(dns_server: &str, domain: &str) -> Result<bool, String> {
    let ps_script = format!(
        r#"
        try {{
            $result = Resolve-DnsName -Name {} -Server {} -DnsOnly -ErrorAction Stop
            if ($result) {{ "OK" }} else {{ "FAIL" }}
        }} catch {{
            "FAIL"
        }}
        "#,
        domain, dns_server
    );

    let result = run_powershell(&ps_script)?;
    Ok(result.trim() == "OK")
}

/// Ejecutar comando PowerShell
fn run_powershell(command: &str) -> Result<String, String> {
    #[cfg(windows)]
    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", command])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .map_err(|e| format!("Error ejecutando PowerShell: {}", e))?;

    #[cfg(not(windows))]
    let output = Command::new("powershell")
        .args(["-NoProfile", "-Command", command])
        .output()
        .map_err(|e| format!("Error ejecutando PowerShell: {}", e))?;

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr);
        Err(format!("PowerShell error: {}", stderr))
    }
}

//! Diagnostic commands module
//!
//! Comandos Tauri para diagnóstico de red.

use serde::{Deserialize, Serialize};
use std::process::Command;
use std::time::Instant;

#[cfg(windows)]
use std::os::windows::process::CommandExt;

#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x08000000;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum FailurePoint {
    None,
    Adapter,
    Router,
    Isp,
    Dns,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum NetworkHealth {
    Excellent,
    Good,
    Fair,
    Poor,
    Bad,
    Down,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DiagnosticResult {
    pub health: NetworkHealth,
    pub score: f64,
    pub failure_point: FailurePoint,
    pub adapter_ok: bool,
    pub adapter_name: String,
    pub router_ok: bool,
    pub router_latency_ms: f64,
    pub isp_ok: bool,
    pub isp_latency_ms: f64,
    pub dns_ok: bool,
    pub dns_latency_ms: f64,
    pub recommendation: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PingResult {
    pub success: bool,
    pub host: String,
    pub latency_ms: Option<f64>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DnsHealthResult {
    pub provider: String,
    pub server: String,
    pub online: bool,
    pub latency_ms: f64,
    pub resolves_correctly: bool,
}

/// Ejecuta diagnóstico completo de 4 fases
#[tauri::command]
pub async fn run_full_diagnostic() -> Result<DiagnosticResult, String> {
    log::info!("Iniciando diagnóstico de red de 4 fases...");
    
    let mut result = DiagnosticResult {
        health: NetworkHealth::Down,
        score: 0.0,
        failure_point: FailurePoint::Adapter,
        adapter_ok: false,
        adapter_name: String::new(),
        router_ok: false,
        router_latency_ms: 0.0,
        isp_ok: false,
        isp_latency_ms: 0.0,
        dns_ok: false,
        dns_latency_ms: 0.0,
        recommendation: String::new(),
    };

    // Phase 1: Check adapter
    log::info!("Fase 1: Verificando adaptador de red...");
    let adapter = check_adapter().await?;
    if adapter.is_none() {
        result.recommendation = "No hay adaptador de red activo. Verifica tu conexión.".to_string();
        log::warn!("Fase 1 FALLIDA: Sin adaptador activo");
        return Ok(result);
    }
    
    result.adapter_ok = true;
    result.adapter_name = adapter.unwrap();
    log::info!("Fase 1 OK: Adaptador '{}'", result.adapter_name);

    // Phase 2: Check router (gateway)
    log::info!("Fase 2: Verificando router/gateway...");
    let gateway = get_gateway().await?;
    if let Some(gw) = gateway {
        if let Some(latency) = ping_host_internal(&gw).await {
            result.router_ok = true;
            result.router_latency_ms = latency;
            result.failure_point = FailurePoint::Isp;
            log::info!("Fase 2 OK: Gateway {} responde en {:.1}ms", gw, latency);
        } else {
            result.recommendation = "No se puede alcanzar el router. Verifica tu conexión local.".to_string();
            log::warn!("Fase 2 FALLIDA: No responde gateway {}", gw);
            return Ok(result);
        }
    } else {
        result.recommendation = "No se encontró gateway. Verifica configuración de red.".to_string();
        log::warn!("Fase 2 FALLIDA: Sin gateway configurado");
        return Ok(result);
    }

    // Phase 3: Check ISP (ping to external IP)
    log::info!("Fase 3: Verificando conexión ISP...");
    if let Some(latency) = ping_host_internal("1.1.1.1").await {
        result.isp_ok = true;
        result.isp_latency_ms = latency;
        result.failure_point = FailurePoint::Dns;
        log::info!("Fase 3 OK: ISP responde en {:.1}ms", latency);
    } else {
        result.recommendation = "Sin conexión a internet. Contacta a tu ISP.".to_string();
        log::warn!("Fase 3 FALLIDA: Sin conexión externa");
        return Ok(result);
    }

    // Phase 4: Check DNS
    log::info!("Fase 4: Verificando resolución DNS...");
    if let Some(latency) = resolve_dns("google.com").await {
        result.dns_ok = true;
        result.dns_latency_ms = latency;
        result.failure_point = FailurePoint::None;
        log::info!("Fase 4 OK: DNS responde en {:.1}ms", latency);
    } else {
        result.recommendation = "DNS no funciona. Prueba cambiar a Cloudflare (1.1.1.1).".to_string();
        log::warn!("Fase 4 FALLIDA: DNS no resuelve");
        return Ok(result);
    }

    // Calculate health based on weighted score
    // Score formula más realista:
    // - Router <50ms = perfecto, <100ms = ok, <200ms = lento
    // - ISP <80ms = perfecto, <150ms = ok, <300ms = lento
    // - DNS <100ms = perfecto, <200ms = ok, <400ms = lento
    
    // Normalizar cada latencia a un score 0-100
    let router_score = (100.0 - (result.router_latency_ms / 2.0)).max(0.0).min(100.0);
    let isp_score = (100.0 - (result.isp_latency_ms / 3.0)).max(0.0).min(100.0);
    let dns_score = (100.0 - (result.dns_latency_ms / 4.0)).max(0.0).min(100.0);
    
    // Promedio ponderado: Router 20%, ISP 30%, DNS 50% 
    let score = (router_score * 0.2) + (isp_score * 0.3) + (dns_score * 0.5);
    result.score = score.round();
    
    result.health = if score >= 90.0 {
        NetworkHealth::Excellent
    } else if score >= 75.0 {
        NetworkHealth::Good
    } else if score >= 50.0 {
        NetworkHealth::Fair
    } else if score >= 25.0 {
        NetworkHealth::Poor
    } else {
        NetworkHealth::Bad
    };

    result.recommendation = match result.health {
        NetworkHealth::Excellent => format!("Tu conexión está funcionando perfectamente. Score: {:.0}/100", score),
        NetworkHealth::Good => format!("Tu conexión está bien. Score: {:.0}/100", score),
        NetworkHealth::Fair => format!("Conexión aceptable. Considera optimizar DNS. Score: {:.0}/100", score),
        NetworkHealth::Poor => format!("Conexión lenta. Optimiza DNS y verifica tu red. Score: {:.0}/100", score),
        NetworkHealth::Bad => format!("Conexión muy lenta. Verifica tu ISP. Score: {:.0}/100", score),
        NetworkHealth::Down => "Sin conexión.".to_string(),
    };

    log::info!("Diagnóstico completo: {:?}, score: {:.1}, latencias: R={:.0}ms I={:.0}ms D={:.0}ms", 
               result.health, score, result.router_latency_ms, result.isp_latency_ms, result.dns_latency_ms);
    Ok(result)
}

/// Check rápido de conectividad
#[tauri::command]
pub async fn quick_check() -> Result<(bool, String), String> {
    if let Some(latency) = ping_host_internal("1.1.1.1").await {
        if latency < 50.0 {
            Ok((true, format!("Conexión OK ({:.0}ms)", latency)))
        } else {
            Ok((true, format!("Conexión lenta ({:.0}ms)", latency)))
        }
    } else {
        Ok((false, "Sin conexión a internet".to_string()))
    }
}

/// Comando Tauri para hacer ping a un host
#[tauri::command]
pub async fn ping_host(host: String) -> Result<PingResult, String> {
    match ping_host_internal(&host).await {
        Some(latency) => Ok(PingResult {
            success: true,
            host,
            latency_ms: Some(latency),
            error: None,
        }),
        None => Ok(PingResult {
            success: false,
            host,
            latency_ms: None,
            error: Some("Host inalcanzable".to_string()),
        }),
    }
}

/// DNS providers para health check
const DNS_HEALTH_PROVIDERS: &[(&str, &str)] = &[
    ("Cloudflare", "1.1.1.1"),
    ("Google", "8.8.8.8"),
    ("Quad9", "9.9.9.9"),
    ("OpenDNS", "208.67.222.222"),
    ("AdGuard", "94.140.14.14"),
    ("CleanBrowsing", "185.228.168.9"),
];

/// Comando Tauri para verificar salud de DNS
#[tauri::command]
pub async fn check_dns_health() -> Result<Vec<DnsHealthResult>, String> {
    let mut results = Vec::new();
    
    for (provider, server) in DNS_HEALTH_PROVIDERS {
        let start = Instant::now();
        
        // Verificar si el servidor responde a ping
        let online = ping_host_internal(server).await.is_some();
        let ping_latency = start.elapsed().as_millis() as f64;
        
        // Verificar si resuelve DNS correctamente
        let resolves = if online {
            resolve_dns_with_server("google.com", server).await
        } else {
            false
        };
        
        results.push(DnsHealthResult {
            provider: provider.to_string(),
            server: server.to_string(),
            online,
            latency_ms: if online { ping_latency } else { 0.0 },
            resolves_correctly: resolves,
        });
    }
    
    // Ordenar por latencia (menores primero)
    results.sort_by(|a, b| {
        if !a.online && !b.online {
            std::cmp::Ordering::Equal
        } else if !a.online {
            std::cmp::Ordering::Greater
        } else if !b.online {
            std::cmp::Ordering::Less
        } else {
            a.latency_ms.partial_cmp(&b.latency_ms).unwrap_or(std::cmp::Ordering::Equal)
        }
    });
    
    Ok(results)
}

/// Resultado del check de un DNS individual
#[derive(Debug, serde::Serialize)]
pub struct SingleDnsHealthResult {
    pub latency_ms: f64,
    pub success: bool,
    pub resolves: bool,
}

/// Check de salud de un servidor DNS específico
#[tauri::command]
pub async fn check_single_dns_health(server: String) -> Result<SingleDnsHealthResult, String> {
    let start = Instant::now();
    
    // Usar resolución DNS real en lugar de ping
    let resolves = resolve_dns_with_server("google.com", &server).await;
    let latency_ms = start.elapsed().as_millis() as f64;
    
    // Si resolvió, consideramos el servidor online
    // Si no resolvió, intentamos ping como fallback
    let success = if resolves {
        true
    } else {
        ping_host_internal(&server).await.is_some()
    };
    
    Ok(SingleDnsHealthResult {
        latency_ms: if success || resolves { latency_ms } else { 999.0 },
        success: success || resolves,
        resolves,
    })
}

/// Función interna para resolver DNS usando un servidor específico
async fn resolve_dns_with_server(domain: &str, dns_server: &str) -> bool {
    #[cfg(windows)]
    let output = Command::new("nslookup")
        .args([domain, dns_server])
        .creation_flags(CREATE_NO_WINDOW)
        .output();
    
    #[cfg(not(windows))]
    let output = Command::new("nslookup")
        .args([domain, dns_server])
        .output();
    
    match output {
        Ok(o) if o.status.success() => {
            let stdout = String::from_utf8_lossy(&o.stdout);
            // Verificar que se obtuvo una respuesta válida
            stdout.contains("Address") && !stdout.contains("can't find")
        }
        _ => false,
    }
}

async fn check_adapter() -> Result<Option<String>, String> {
    #[cfg(windows)]
    let output = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1 -ExpandProperty Name",
        ])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .map_err(|e| e.to_string())?;

    #[cfg(not(windows))]
    let output = Command::new("ip")
        .args(["link", "show", "up"])
        .output()
        .map_err(|e| e.to_string())?;

    let name = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if name.is_empty() {
        Ok(None)
    } else {
        Ok(Some(name))
    }
}

async fn get_gateway() -> Result<Option<String>, String> {
    #[cfg(windows)]
    let output = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object -First 1).NextHop",
        ])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .map_err(|e| e.to_string())?;

    #[cfg(not(windows))]
    let output = Command::new("ip")
        .args(["route", "show", "default"])
        .output()
        .map_err(|e| e.to_string())?;

    let gateway = String::from_utf8_lossy(&output.stdout).trim().to_string();
    
    #[cfg(not(windows))]
    let gateway = gateway
        .split_whitespace()
        .nth(2)
        .unwrap_or("")
        .to_string();
    
    if gateway.is_empty() {
        Ok(None)
    } else {
        Ok(Some(gateway))
    }
}

/// Función interna para ping (usada por diagnósticos)
async fn ping_host_internal(host: &str) -> Option<f64> {
    let start = Instant::now();
    
    #[cfg(windows)]
    let output = Command::new("ping")
        .args(["-n", "1", "-w", "2000", host])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .ok()?;
    
    #[cfg(not(windows))]
    let output = Command::new("ping")
        .args(["-c", "1", "-W", "2", host])
        .output()
        .ok()?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        // Parse latency from ping output
        if let Some(time_str) = stdout.split("time=").nth(1) {
            if let Some(ms_str) = time_str.split("ms").next() {
                if let Ok(ms) = ms_str.trim().replace('<', "").parse::<f64>() {
                    return Some(ms);
                }
            }
        }
        // Fallback to measured time
        Some(start.elapsed().as_millis() as f64)
    } else {
        None
    }
}

async fn resolve_dns(domain: &str) -> Option<f64> {
    let start = Instant::now();
    
    #[cfg(windows)]
    let output = Command::new("nslookup")
        .args([domain])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .ok()?;
    
    #[cfg(not(windows))]
    let output = Command::new("nslookup")
        .args([domain])
        .output()
        .ok()?;

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        if stdout.contains("Address") {
            return Some(start.elapsed().as_millis() as f64);
        }
    }
    None
}

//! Diagnostic commands module
//!
//! Comandos Tauri para diagnóstico de red.

use serde::{Deserialize, Serialize};
use std::process::Command;
use std::time::Instant;

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

/// Ejecuta diagnóstico completo de 4 fases
#[tauri::command]
pub async fn run_full_diagnostic() -> Result<DiagnosticResult, String> {
    let mut result = DiagnosticResult {
        health: NetworkHealth::Down,
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
    let adapter = check_adapter().await?;
    if adapter.is_none() {
        result.recommendation = "No hay adaptador de red activo. Verifica tu conexión.".to_string();
        return Ok(result);
    }
    
    result.adapter_ok = true;
    result.adapter_name = adapter.unwrap();

    // Phase 2: Check router (gateway)
    let gateway = get_gateway().await?;
    if let Some(gw) = gateway {
        if let Some(latency) = ping_host(&gw).await {
            result.router_ok = true;
            result.router_latency_ms = latency;
            result.failure_point = FailurePoint::Isp;
        } else {
            result.recommendation = "No se puede alcanzar el router. Verifica tu conexión local.".to_string();
            return Ok(result);
        }
    }

    // Phase 3: Check ISP (ping to external IP)
    if let Some(latency) = ping_host("1.1.1.1").await {
        result.isp_ok = true;
        result.isp_latency_ms = latency;
        result.failure_point = FailurePoint::Dns;
    } else {
        result.recommendation = "Sin conexión a internet. Contacta a tu ISP.".to_string();
        return Ok(result);
    }

    // Phase 4: Check DNS
    if let Some(latency) = resolve_dns("google.com").await {
        result.dns_ok = true;
        result.dns_latency_ms = latency;
        result.failure_point = FailurePoint::None;
    } else {
        result.recommendation = "DNS no funciona. Prueba cambiar a Cloudflare (1.1.1.1).".to_string();
        return Ok(result);
    }

    // Calculate health
    let max_latency = result.router_latency_ms
        .max(result.isp_latency_ms)
        .max(result.dns_latency_ms);

    result.health = if max_latency < 20.0 {
        NetworkHealth::Excellent
    } else if max_latency < 50.0 {
        NetworkHealth::Good
    } else if max_latency < 100.0 {
        NetworkHealth::Fair
    } else if max_latency < 200.0 {
        NetworkHealth::Poor
    } else {
        NetworkHealth::Bad
    };

    result.recommendation = match result.health {
        NetworkHealth::Excellent => "Tu conexión está funcionando perfectamente.".to_string(),
        NetworkHealth::Good => "Tu conexión está bien.".to_string(),
        NetworkHealth::Fair => "Conexión aceptable, pero podría mejorar.".to_string(),
        NetworkHealth::Poor => "Conexión lenta. Considera optimizar DNS.".to_string(),
        NetworkHealth::Bad => "Conexión muy lenta. Verifica tu ISP.".to_string(),
        NetworkHealth::Down => "Sin conexión.".to_string(),
    };

    Ok(result)
}

/// Check rápido de conectividad
#[tauri::command]
pub async fn quick_check() -> Result<(bool, String), String> {
    if let Some(latency) = ping_host("1.1.1.1").await {
        if latency < 50.0 {
            Ok((true, format!("Conexión OK ({:.0}ms)", latency)))
        } else {
            Ok((true, format!("Conexión lenta ({:.0}ms)", latency)))
        }
    } else {
        Ok((false, "Sin conexión a internet".to_string()))
    }
}

async fn check_adapter() -> Result<Option<String>, String> {
    let output = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            "Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1 -ExpandProperty Name",
        ])
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
    let output = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Select-Object -First 1).NextHop",
        ])
        .output()
        .map_err(|e| e.to_string())?;

    let gateway = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if gateway.is_empty() {
        Ok(None)
    } else {
        Ok(Some(gateway))
    }
}

async fn ping_host(host: &str) -> Option<f64> {
    let start = Instant::now();
    
    let output = Command::new("ping")
        .args(["-n", "1", "-w", "2000", host])
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

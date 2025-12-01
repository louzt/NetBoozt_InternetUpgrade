//! Optimizer commands module
//!
//! Comandos Tauri para optimizaciones TCP/IP.

use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct TcpSettings {
    pub autotuning: String,
    pub rss: String,
    pub rsc: String,
    pub ecn: String,
    pub timestamps: String,
    pub chimney: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum OptimizationProfile {
    Conservative,
    Balanced,
    Aggressive,
}

/// Obtiene configuración TCP actual
#[tauri::command]
pub async fn get_current_settings() -> Result<TcpSettings, String> {
    let output = Command::new("netsh")
        .args(["int", "tcp", "show", "global"])
        .output()
        .map_err(|e| e.to_string())?;

    let stdout = String::from_utf8_lossy(&output.stdout);

    fn extract_value(text: &str, key: &str) -> String {
        for line in text.lines() {
            if line.contains(key) {
                if let Some(value) = line.split(':').nth(1) {
                    return value.trim().to_string();
                }
            }
        }
        "unknown".to_string()
    }

    Ok(TcpSettings {
        autotuning: extract_value(&stdout, "Receive Window Auto-Tuning"),
        rss: extract_value(&stdout, "Receive-Side Scaling"),
        rsc: extract_value(&stdout, "Receive Segment Coalescing"),
        ecn: extract_value(&stdout, "ECN Capability"),
        timestamps: extract_value(&stdout, "Timestamps"),
        chimney: extract_value(&stdout, "Chimney Offload"),
    })
}

/// Aplica perfil de optimización
#[tauri::command]
pub async fn apply_profile(profile: OptimizationProfile) -> Result<Vec<String>, String> {
    let mut applied = Vec::new();
    
    match profile {
        OptimizationProfile::Conservative => {
            // Solo optimizaciones seguras
            run_netsh("int tcp set global rss=enabled")?;
            applied.push("RSS enabled".to_string());
            
            run_netsh("int tcp set global rsc=enabled")?;
            applied.push("RSC enabled".to_string());
            
            run_netsh("int tcp set global autotuninglevel=normal")?;
            applied.push("Autotuning normal".to_string());
        }
        OptimizationProfile::Balanced => {
            // Incluye ECN y timestamps
            run_netsh("int tcp set global rss=enabled")?;
            applied.push("RSS enabled".to_string());
            
            run_netsh("int tcp set global rsc=enabled")?;
            applied.push("RSC enabled".to_string());
            
            run_netsh("int tcp set global autotuninglevel=normal")?;
            applied.push("Autotuning normal".to_string());
            
            run_netsh("int tcp set global ecncapability=enabled")?;
            applied.push("ECN enabled".to_string());
            
            run_netsh("int tcp set global timestamps=enabled")?;
            applied.push("Timestamps enabled".to_string());
            
            // Registry settings (require admin)
            set_registry_dword("EnableHyStart", 1)?;
            applied.push("HyStart++ enabled".to_string());
            
            set_registry_dword("EnablePrr", 1)?;
            applied.push("PRR enabled".to_string());
        }
        OptimizationProfile::Aggressive => {
            // Todas las optimizaciones
            run_netsh("int tcp set global rss=enabled")?;
            applied.push("RSS enabled".to_string());
            
            run_netsh("int tcp set global rsc=enabled")?;
            applied.push("RSC enabled".to_string());
            
            run_netsh("int tcp set global autotuninglevel=normal")?;
            applied.push("Autotuning normal".to_string());
            
            run_netsh("int tcp set global ecncapability=enabled")?;
            applied.push("ECN enabled".to_string());
            
            run_netsh("int tcp set global timestamps=enabled")?;
            applied.push("Timestamps enabled".to_string());
            
            run_netsh("int tcp set global chimney=disabled")?;
            applied.push("Chimney disabled".to_string());
            
            // Registry settings
            set_registry_dword("EnableHyStart", 1)?;
            applied.push("HyStart++ enabled".to_string());
            
            set_registry_dword("EnablePrr", 1)?;
            applied.push("PRR enabled".to_string());
            
            set_registry_dword("EnableTFO", 1)?;
            applied.push("TCP Fast Open enabled".to_string());
            
            set_registry_dword("EnableWsd", 0)?;
            applied.push("TCP Pacing enabled".to_string());
            
            set_registry_dword("TcpInitialRto", 1000)?;
            applied.push("Initial RTO reduced".to_string());
        }
    }
    
    Ok(applied)
}

/// Restaura valores por defecto
#[tauri::command]
pub async fn reset_to_defaults() -> Result<Vec<String>, String> {
    let mut reset = Vec::new();
    
    run_netsh("int tcp set global autotuninglevel=normal")?;
    reset.push("Autotuning reset".to_string());
    
    run_netsh("int tcp set global ecncapability=default")?;
    reset.push("ECN reset".to_string());
    
    run_netsh("int tcp set global timestamps=disabled")?;
    reset.push("Timestamps reset".to_string());
    
    // Delete registry keys
    delete_registry_value("EnableHyStart")?;
    reset.push("HyStart++ removed".to_string());
    
    delete_registry_value("EnablePrr")?;
    reset.push("PRR removed".to_string());
    
    delete_registry_value("EnableTFO")?;
    reset.push("TCP Fast Open removed".to_string());
    
    Ok(reset)
}

fn run_netsh(args: &str) -> Result<(), String> {
    let full_args: Vec<&str> = args.split_whitespace().collect();
    let output = Command::new("netsh")
        .args(&full_args)
        .output()
        .map_err(|e| e.to_string())?;
    
    if output.status.success() {
        Ok(())
    } else {
        Err(format!("netsh {} failed", args))
    }
}

fn set_registry_dword(name: &str, value: u32) -> Result<(), String> {
    let command = format!(
        r#"reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v {} /t REG_DWORD /d {} /f"#,
        name, value
    );
    
    let output = Command::new("cmd")
        .args(["/c", &command])
        .output()
        .map_err(|e| e.to_string())?;
    
    if output.status.success() {
        Ok(())
    } else {
        Err(format!("Failed to set registry {}", name))
    }
}

fn delete_registry_value(name: &str) -> Result<(), String> {
    let command = format!(
        r#"reg delete "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v {} /f"#,
        name
    );
    
    // Ignore error if value doesn't exist
    let _ = Command::new("cmd")
        .args(["/c", &command])
        .output();
    
    Ok(())
}

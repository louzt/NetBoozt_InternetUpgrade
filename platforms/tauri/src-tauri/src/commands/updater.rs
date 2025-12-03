//! Updater commands
//!
//! Comandos para verificar, descargar e instalar actualizaciones.

use std::path::PathBuf;
use std::process::Command;
use tauri::api::path::download_dir;

/// Descargar actualización a la carpeta de descargas
#[tauri::command]
pub async fn download_update(url: String, filename: String) -> Result<String, String> {
    log::info!("Descargando actualización desde: {}", url);
    
    // Obtener carpeta de descargas
    let download_path = download_dir()
        .ok_or_else(|| "No se pudo obtener la carpeta de descargas".to_string())?
        .join(&filename);
    
    // Descargar archivo usando reqwest
    let response = reqwest::get(&url)
        .await
        .map_err(|e| format!("Error descargando: {}", e))?;
    
    if !response.status().is_success() {
        return Err(format!("Error HTTP: {}", response.status()));
    }
    
    let bytes = response
        .bytes()
        .await
        .map_err(|e| format!("Error leyendo respuesta: {}", e))?;
    
    // Guardar archivo
    std::fs::write(&download_path, bytes)
        .map_err(|e| format!("Error guardando archivo: {}", e))?;
    
    log::info!("Actualización descargada en: {:?}", download_path);
    
    Ok(download_path.to_string_lossy().to_string())
}

/// Instalar actualización (ejecutar instalador)
#[tauri::command]
pub async fn install_update(path: String) -> Result<(), String> {
    log::info!("Instalando actualización: {}", path);
    
    let path = PathBuf::from(&path);
    
    if !path.exists() {
        return Err("El archivo de instalación no existe".to_string());
    }
    
    #[cfg(windows)]
    {
        // Ejecutar instalador con elevación
        let result = Command::new("powershell")
            .args([
                "-NoProfile",
                "-Command",
                &format!("Start-Process '{}' -Verb RunAs", path.display())
            ])
            .spawn();
        
        match result {
            Ok(_) => {
                log::info!("Instalador ejecutado con éxito");
                // Opcional: cerrar la app actual después de un delay
                Ok(())
            }
            Err(e) => {
                log::error!("Error ejecutando instalador: {}", e);
                Err(format!("Error ejecutando instalador: {}", e))
            }
        }
    }
    
    #[cfg(not(windows))]
    {
        Err("Instalación automática solo disponible en Windows".to_string())
    }
}

/// Obtener ruta de descargas
#[tauri::command]
pub fn get_downloads_path() -> Result<String, String> {
    download_dir()
        .map(|p| p.to_string_lossy().to_string())
        .ok_or_else(|| "No se pudo obtener la carpeta de descargas".to_string())
}

/// Verificar si existe un archivo
#[tauri::command]
pub fn file_exists(path: String) -> bool {
    PathBuf::from(path).exists()
}

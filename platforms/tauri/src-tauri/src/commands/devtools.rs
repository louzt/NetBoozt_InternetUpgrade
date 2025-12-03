//! DevTools Commands
//!
//! Comandos Tauri para las utilidades de desarrollo:
//! - HTTP requests (curl-like)
//! - Ping con múltiples paquetes
//! - Traceroute
//! - Port scanning
//! - Security headers check

use serde::Serialize;
use std::collections::HashMap;
use std::os::windows::process::CommandExt;
use std::process::Command;
use std::time::Instant;

// ============================================
// HTTP REQUEST (cURL-like)
// ============================================

#[derive(Debug, Serialize)]
pub struct HttpResponse {
    pub status: u16,
    pub headers: HashMap<String, String>,
    pub body: String,
    pub time_ms: f64,
}

#[tauri::command]
pub async fn http_request(
    url: String,
    method: String,
    headers: Option<HashMap<String, String>>,
    body: Option<String>,
) -> Result<HttpResponse, String> {
    let start = Instant::now();
    
    // Usar PowerShell Invoke-WebRequest para hacer la petición
    let mut ps_script = format!(
        r#"
        $ErrorActionPreference = 'Stop'
        try {{
            $headers = @{{}}
            $method = '{}'
            $uri = '{}'
        "#,
        method, url
    );
    
    // Agregar headers si existen
    if let Some(hdrs) = &headers {
        for (key, value) in hdrs {
            ps_script.push_str(&format!(
                r#"$headers['{}'] = '{}'{}"#,
                key.replace("'", "''"),
                value.replace("'", "''"),
                "\n"
            ));
        }
    }
    
    // Agregar body si existe y no es GET/HEAD
    let body_param = if method != "GET" && method != "HEAD" {
        if let Some(b) = &body {
            format!(r#"-Body '{}'"#, b.replace("'", "''"))
        } else {
            String::new()
        }
    } else {
        String::new()
    };
    
    ps_script.push_str(&format!(
        r#"
            $response = Invoke-WebRequest -Uri $uri -Method $method -Headers $headers {} -UseBasicParsing -TimeoutSec 30
            
            $result = @{{
                StatusCode = $response.StatusCode
                Headers = @{{}}
                Content = $response.Content
            }}
            
            foreach ($key in $response.Headers.Keys) {{
                $result.Headers[$key] = $response.Headers[$key] -join ', '
            }}
            
            $result | ConvertTo-Json -Depth 3
        }} catch {{
            @{{
                Error = $_.Exception.Message
                StatusCode = 0
            }} | ConvertTo-Json
        }}
        "#,
        body_param
    ));
    
    let output = Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &ps_script])
        .creation_flags(0x08000000) // CREATE_NO_WINDOW
        .output()
        .map_err(|e| format!("Error ejecutando PowerShell: {}", e))?;
    
    let elapsed = start.elapsed().as_secs_f64() * 1000.0;
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    // Parsear el JSON de respuesta
    if let Ok(json) = serde_json::from_str::<serde_json::Value>(&stdout) {
        if let Some(error) = json.get("Error") {
            return Err(error.as_str().unwrap_or("Error desconocido").to_string());
        }
        
        let status = json.get("StatusCode")
            .and_then(|v| v.as_u64())
            .unwrap_or(0) as u16;
        
        let mut headers_map = HashMap::new();
        if let Some(hdrs) = json.get("Headers").and_then(|v| v.as_object()) {
            for (k, v) in hdrs {
                headers_map.insert(k.clone(), v.as_str().unwrap_or("").to_string());
            }
        }
        
        let body_content = json.get("Content")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        
        Ok(HttpResponse {
            status,
            headers: headers_map,
            body: body_content,
            time_ms: elapsed,
        })
    } else {
        Err(format!("Error parseando respuesta: {}", stdout))
    }
}

// ============================================
// PING CON MÚLTIPLES PAQUETES
// ============================================

#[derive(Debug, Serialize)]
pub struct PingPacket {
    pub seq: u32,
    pub ttl: u32,
    pub time: f64,
}

#[derive(Debug, Serialize)]
pub struct PingStats {
    pub min: f64,
    pub max: f64,
    pub avg: f64,
    pub loss: f64,
}

#[derive(Debug, Serialize)]
pub struct PingMultiResult {
    pub results: Vec<PingPacket>,
    pub stats: PingStats,
}

#[tauri::command]
pub async fn ping_multi(host: String, count: u32) -> Result<PingMultiResult, String> {
    let ps_script = format!(
        r#"
        $results = @()
        $host_target = '{}'
        $count = {}
        $success = 0
        $times = @()
        
        for ($i = 1; $i -le $count; $i++) {{
            try {{
                $ping = Test-Connection -ComputerName $host_target -Count 1 -ErrorAction Stop
                $results += @{{
                    seq = $i
                    ttl = $ping.ResponseTimeToLive
                    time = $ping.ResponseTime
                }}
                $times += $ping.ResponseTime
                $success++
            }} catch {{
                $results += @{{
                    seq = $i
                    ttl = 0
                    time = -1
                }}
            }}
        }}
        
        $stats = @{{
            min = if ($times.Count -gt 0) {{ ($times | Measure-Object -Minimum).Minimum }} else {{ 0 }}
            max = if ($times.Count -gt 0) {{ ($times | Measure-Object -Maximum).Maximum }} else {{ 0 }}
            avg = if ($times.Count -gt 0) {{ ($times | Measure-Object -Average).Average }} else {{ 0 }}
            loss = [math]::Round((($count - $success) / $count) * 100, 1)
        }}
        
        @{{
            results = $results
            stats = $stats
        }} | ConvertTo-Json -Depth 3
        "#,
        host, count
    );
    
    let output = Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &ps_script])
        .creation_flags(0x08000000)
        .output()
        .map_err(|e| format!("Error ejecutando ping: {}", e))?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    if let Ok(json) = serde_json::from_str::<serde_json::Value>(&stdout) {
        let mut results = Vec::new();
        
        if let Some(res_array) = json.get("results").and_then(|v| v.as_array()) {
            for item in res_array {
                let seq = item.get("seq").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
                let ttl = item.get("ttl").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
                let time = item.get("time").and_then(|v| v.as_f64()).unwrap_or(-1.0);
                
                if time >= 0.0 {
                    results.push(PingPacket { seq, ttl, time });
                }
            }
        }
        
        let stats = if let Some(s) = json.get("stats") {
            PingStats {
                min: s.get("min").and_then(|v| v.as_f64()).unwrap_or(0.0),
                max: s.get("max").and_then(|v| v.as_f64()).unwrap_or(0.0),
                avg: s.get("avg").and_then(|v| v.as_f64()).unwrap_or(0.0),
                loss: s.get("loss").and_then(|v| v.as_f64()).unwrap_or(0.0),
            }
        } else {
            PingStats { min: 0.0, max: 0.0, avg: 0.0, loss: 100.0 }
        };
        
        Ok(PingMultiResult { results, stats })
    } else {
        Err("Error parseando resultados de ping".to_string())
    }
}

// ============================================
// TRACEROUTE
// ============================================

#[derive(Debug, Serialize)]
pub struct TraceHop {
    pub hop: u32,
    pub ip: String,
    pub hostname: Option<String>,
    pub time: Vec<f64>,
}

#[derive(Debug, Serialize)]
pub struct TracerouteResult {
    pub hops: Vec<TraceHop>,
}

#[tauri::command]
pub async fn traceroute(host: String, max_hops: Option<u32>) -> Result<TracerouteResult, String> {
    let max = max_hops.unwrap_or(30);
    
    let ps_script = format!(
        r#"
        $results = @()
        $output = tracert -h {} -w 1000 {} 2>&1
        
        $hopNum = 0
        foreach ($line in $output) {{
            if ($line -match '^\s*(\d+)\s+') {{
                $hopNum = [int]$Matches[1]
                $times = @()
                
                # Extraer tiempos (pueden ser <1 ms, X ms, o *)
                $timeMatches = [regex]::Matches($line, '(<?\d+)\s*ms|(\*)')
                foreach ($match in $timeMatches) {{
                    if ($match.Groups[1].Success) {{
                        $times += [double]$match.Groups[1].Value
                    }} elseif ($match.Groups[2].Success) {{
                        $times += -1
                    }}
                }}
                
                # Extraer IP y hostname
                $ip = ''
                $hostname = $null
                
                if ($line -match '\[([^\]]+)\]') {{
                    $ip = $Matches[1]
                    if ($line -match '(\S+)\s+\[') {{
                        $hostname = $Matches[1]
                    }}
                }} elseif ($line -match '(\d+\.\d+\.\d+\.\d+)') {{
                    $ip = $Matches[1]
                }}
                
                if ($ip -or $times.Count -gt 0) {{
                    $results += @{{
                        hop = $hopNum
                        ip = if ($ip) {{ $ip }} else {{ '*' }}
                        hostname = $hostname
                        time = $times | Where-Object {{ $_ -ge 0 }}
                    }}
                }}
            }}
        }}
        
        @{{ hops = $results }} | ConvertTo-Json -Depth 3
        "#,
        max, host
    );
    
    let output = Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &ps_script])
        .creation_flags(0x08000000)
        .output()
        .map_err(|e| format!("Error ejecutando traceroute: {}", e))?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    if let Ok(json) = serde_json::from_str::<serde_json::Value>(&stdout) {
        let mut hops = Vec::new();
        
        if let Some(hops_array) = json.get("hops").and_then(|v| v.as_array()) {
            for item in hops_array {
                let hop = item.get("hop").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
                let ip = item.get("ip").and_then(|v| v.as_str()).unwrap_or("*").to_string();
                let hostname = item.get("hostname").and_then(|v| v.as_str()).map(|s| s.to_string());
                
                let mut times = Vec::new();
                if let Some(time_array) = item.get("time").and_then(|v| v.as_array()) {
                    for t in time_array {
                        if let Some(time_val) = t.as_f64() {
                            times.push(time_val);
                        }
                    }
                }
                
                hops.push(TraceHop { hop, ip, hostname, time: times });
            }
        }
        
        Ok(TracerouteResult { hops })
    } else {
        Err("Error parseando resultados de traceroute".to_string())
    }
}

// ============================================
// PORT SCANNER
// ============================================

#[derive(Debug, Serialize)]
pub struct PortResult {
    pub port: u16,
    pub status: String, // "open", "closed", "filtered"
}

#[derive(Debug, Serialize)]
pub struct ScanPortsResult {
    pub results: Vec<PortResult>,
}

#[tauri::command]
pub async fn scan_ports(host: String, ports: Vec<u16>) -> Result<ScanPortsResult, String> {
    let ports_str = ports.iter()
        .map(|p| p.to_string())
        .collect::<Vec<_>>()
        .join(",");
    
    let ps_script = format!(
        r#"
        $host_target = '{}'
        $ports = @({})
        $results = @()
        
        foreach ($port in $ports) {{
            $status = 'closed'
            try {{
                $tcp = New-Object System.Net.Sockets.TcpClient
                $connect = $tcp.BeginConnect($host_target, $port, $null, $null)
                $wait = $connect.AsyncWaitHandle.WaitOne(1000, $false)
                
                if ($wait) {{
                    try {{
                        $tcp.EndConnect($connect)
                        $status = 'open'
                    }} catch {{
                        $status = 'closed'
                    }}
                }} else {{
                    $status = 'filtered'
                }}
                
                $tcp.Close()
            }} catch {{
                $status = 'closed'
            }}
            
            $results += @{{
                port = $port
                status = $status
            }}
        }}
        
        @{{ results = $results }} | ConvertTo-Json -Depth 2
        "#,
        host, ports_str
    );
    
    let output = Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &ps_script])
        .creation_flags(0x08000000)
        .output()
        .map_err(|e| format!("Error ejecutando port scan: {}", e))?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    if let Ok(json) = serde_json::from_str::<serde_json::Value>(&stdout) {
        let mut results = Vec::new();
        
        if let Some(res_array) = json.get("results").and_then(|v| v.as_array()) {
            for item in res_array {
                let port = item.get("port").and_then(|v| v.as_u64()).unwrap_or(0) as u16;
                let status = item.get("status").and_then(|v| v.as_str()).unwrap_or("closed").to_string();
                results.push(PortResult { port, status });
            }
        }
        
        Ok(ScanPortsResult { results })
    } else {
        Err("Error parseando resultados del scan".to_string())
    }
}

// ============================================
// GET HEADERS (Security Headers Check)
// ============================================

#[derive(Debug, Serialize)]
pub struct GetHeadersResult {
    pub headers: HashMap<String, String>,
}

#[tauri::command]
pub async fn get_headers(url: String) -> Result<GetHeadersResult, String> {
    let ps_script = format!(
        r#"
        $ErrorActionPreference = 'Stop'
        try {{
            $response = Invoke-WebRequest -Uri '{}' -Method HEAD -UseBasicParsing -TimeoutSec 10
            $headers = @{{}}
            
            foreach ($key in $response.Headers.Keys) {{
                $headers[$key] = $response.Headers[$key] -join ', '
            }}
            
            @{{ headers = $headers }} | ConvertTo-Json -Depth 2
        }} catch {{
            # Si HEAD falla, intentar con GET
            try {{
                $response = Invoke-WebRequest -Uri '{}' -Method GET -UseBasicParsing -TimeoutSec 10
                $headers = @{{}}
                
                foreach ($key in $response.Headers.Keys) {{
                    $headers[$key] = $response.Headers[$key] -join ', '
                }}
                
                @{{ headers = $headers }} | ConvertTo-Json -Depth 2
            }} catch {{
                @{{ error = $_.Exception.Message }} | ConvertTo-Json
            }}
        }}
        "#,
        url, url
    );
    
    let output = Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &ps_script])
        .creation_flags(0x08000000)
        .output()
        .map_err(|e| format!("Error obteniendo headers: {}", e))?;
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    if let Ok(json) = serde_json::from_str::<serde_json::Value>(&stdout) {
        if let Some(error) = json.get("error") {
            return Err(error.as_str().unwrap_or("Error desconocido").to_string());
        }
        
        let mut headers = HashMap::new();
        if let Some(hdrs) = json.get("headers").and_then(|v| v.as_object()) {
            for (k, v) in hdrs {
                headers.insert(k.clone(), v.as_str().unwrap_or("").to_string());
            }
        }
        
        Ok(GetHeadersResult { headers })
    } else {
        Err("Error parseando headers".to_string())
    }
}

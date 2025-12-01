# NetBoozt Development Tools

Scripts para desarrollo que **NO** se suben a GitHub.

## 📸 Screenshot Generator

Genera capturas automáticas del GUI para documentación.

### Setup (solo dev)
```powershell
# Instalar dependencias (gitignored)
pip install playwright pillow
playwright install chromium
```

### Uso
```powershell
python tools/generate_screenshots.py
```

Genera:
- `docs/assets/screenshots/*.png` - Screenshots completos
- `docs/assets/screenshots/thumbs/*.png` - Thumbnails (400x300)

**Nota**: Screenshots se gitignorean. Para actualizarlos en GitHub, súbelos manualmente a VPS o usa GitHub LFS.

## 🎨 Asset Management

### Logo LOUST
Ubicación: `docs/assets/logo/`
- `LGOLST_WHITE.png` - Logo principal
- `favicon.ico` - Favicon (32x32)
- `favicon-16x16.png` - Favicon pequeño
- `favicon-32x32.png` - Favicon mediano

### Hosting Options

#### 1. GitHub LFS (Large File Storage)
Para archivos >1MB:
```bash
git lfs track "docs/assets/screenshots/*.png"
git add .gitattributes
git commit -m "Track screenshots with LFS"
```

#### 2. VPS Hosting (Recomendado)
Host en `https://vps.loust.pro:999/netboozt/assets/`

```bash
# Subir a VPS
scp -r docs/assets/* user@vps.loust.pro:/home/netboozt-assets/

# Nginx config
location /netboozt/assets/ {
    alias /home/netboozt-assets/;
    autoindex on;
}
```

#### 3. GitHub Releases
Para versiones estables, adjuntar screenshots en releases.

### Asset URLs en README
```markdown
![Main Window](https://vps.loust.pro:999/netboozt/assets/screenshots/main_window.png)
```

O con GitHub:
```markdown
![Main Window](docs/assets/screenshots/main_window.png)
```

# Asset Hosting Strategy

## 📁 Asset Types

NetBoozt has three types of assets:

### 1. **Small Assets** (< 100KB)
- Favicons (favicon.ico, *.png)
- Logos (netboozt_icon.png, LGOLST_WHITE.png)
- **Strategy**: ✅ **Commit to Git** (tracked in repo)

### 2. **Medium Assets** (100KB - 5MB)
- Screenshots (GUI captures)
- Thumbnails
- **Strategy**: ⚠️ **Git LFS or VPS hosting**

### 3. **Large Assets** (> 5MB)
- Video demos
- High-res recordings
- **Strategy**: 🚫 **Never commit** - VPS or CDN only

---

## 🌍 Hosting Options

### Option 1: GitHub Repository (Recommended for Small Assets)

**Pros:**
- ✅ Version controlled
- ✅ Always available with repo
- ✅ Free (< 1GB total)
- ✅ Fast for users cloning

**Cons:**
- ❌ Bloats repository size
- ❌ Slow for large files
- ❌ 100MB file size limit

**Best for:**
- Logos, favicons
- Small diagrams
- Icons

**Implementation:**
```bash
# Already done - commit normally
git add docs/assets/logo/
git commit -m "Add LOUST logo and favicons"
```

---

### Option 2: GitHub LFS (Large File Storage)

**Pros:**
- ✅ Version controlled
- ✅ Doesn't bloat repo
- ✅ Integrated with GitHub

**Cons:**
- ⚠️ 1GB free bandwidth/month
- ⚠️ $5/month for 50GB
- ⚠️ Requires LFS client

**Best for:**
- Screenshots (if committing them)
- Medium-sized images

**Implementation:**
```bash
# Install Git LFS
git lfs install

# Track screenshot files
git lfs track "docs/assets/screenshots/*.png"
git lfs track "docs/assets/screenshots/thumbs/*.png"

# Commit .gitattributes
git add .gitattributes
git commit -m "Track screenshots with LFS"

# Add and commit files
git add docs/assets/screenshots/
git commit -m "Add GUI screenshots via LFS"
git push origin main
```

**Verify LFS:**
```bash
git lfs ls-files
# Should show tracked files
```

---

### Option 3: VPS Hosting (Recommended for NetBoozt)

**Pros:**
- ✅ Unlimited bandwidth (your server)
- ✅ Full control
- ✅ Can use custom domain
- ✅ Fast with CDN

**Cons:**
- ⚠️ Requires server setup
- ⚠️ Maintenance needed
- ⚠️ Separate from repo

**Best for:**
- Screenshots
- Videos
- High-res images
- Any files not needing version control

---

## 🖥️ VPS Setup for NetBoozt Assets

### Server: LOUST VPS (Tunnel Port 999)

#### Directory Structure
```
/home/netboozt-assets/
├── screenshots/
│   ├── main_window.png
│   ├── optimizations_tab.png
│   ├── profiles_tab.png
│   └── thumbs/
│       ├── main_window.png
│       └── ...
├── videos/
│   ├── demo_v1.0.0.mp4
│   └── tutorial.mp4
└── logos/
    ├── LGOLST_WHITE.png
    └── netboozt_icon.png
```

#### Upload Command
```powershell
# From Windows (NetBoozt project)
scp -P 999 -r docs/assets/screenshots/* user@vps.loust.pro:/home/netboozt-assets/screenshots/

# Or use rsync for incremental updates
rsync -avz -e "ssh -p 999" docs/assets/screenshots/ user@vps.loust.pro:/home/netboozt-assets/screenshots/
```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/netboozt-assets

server {
    listen 999 ssl;
    server_name vps.loust.pro;
    
    # SSL config (existing tunnel)
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Assets location
    location /netboozt/assets/ {
        alias /home/netboozt-assets/;
        autoindex on;  # Optional: directory listing
        
        # CORS for GitHub Pages
        add_header Access-Control-Allow-Origin "*";
        
        # Cache headers
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable:**
```bash
sudo ln -s /etc/nginx/sites-available/netboozt-assets /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Access URLs
```
https://vps.loust.pro:999/netboozt/assets/screenshots/main_window.png
https://vps.loust.pro:999/netboozt/assets/videos/demo_v1.0.0.mp4
```

---

## 📝 Usage in Documentation

### GitHub Repo Assets (Logos)
```markdown
![NetBoozt Logo](docs/assets/logo/netboozt_icon.png)
![LOUST](docs/assets/logo/LGOLST_WHITE.png)
```

### VPS Assets (Screenshots)
```markdown
![Main Window](https://vps.loust.pro:999/netboozt/assets/screenshots/main_window.png)
![Optimizations](https://vps.loust.pro:999/netboozt/assets/screenshots/optimizations_tab.png)
```

### Hybrid Approach (Best Practice)
```markdown
<!-- README.md -->
<div align="center">

![Logo](docs/assets/logo/netboozt_icon.png)

## Screenshots

![Main Window](https://vps.loust.pro:999/netboozt/assets/screenshots/main_window.png)

</div>
```

---

## 🔄 Automated Upload Script

Create `tools/upload_assets.ps1`:

```powershell
# NetBoozt Asset Upload Script
# Uploads screenshots and media to VPS

param(
    [string]$VPS = "vps.loust.pro",
    [int]$Port = 999,
    [string]$User = "netboozt",
    [string]$RemotePath = "/home/netboozt-assets"
)

Write-Host "🚀 NetBoozt Asset Upload" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

$LocalAssets = "docs\assets\screenshots"

# Check if assets exist
if (-not (Test-Path $LocalAssets)) {
    Write-Host "❌ No assets found: $LocalAssets" -ForegroundColor Red
    exit 1
}

# Upload with rsync
Write-Host "`n📤 Uploading screenshots..." -ForegroundColor Yellow
$rsyncCmd = "rsync -avz -e 'ssh -p $Port' $LocalAssets/ ${User}@${VPS}:${RemotePath}/screenshots/"

# Execute (requires rsync for Windows or WSL)
if (Get-Command rsync -ErrorAction SilentlyContinue) {
    Invoke-Expression $rsyncCmd
} else {
    Write-Host "⚠️  rsync not found, using scp..." -ForegroundColor Yellow
    scp -P $Port -r "$LocalAssets\*" "${User}@${VPS}:${RemotePath}/screenshots/"
}

Write-Host "`n✅ Upload complete!" -ForegroundColor Green
Write-Host "🔗 Access at: https://${VPS}:${Port}/netboozt/assets/screenshots/" -ForegroundColor Cyan
```

**Usage:**
```powershell
.\tools\upload_assets.ps1
```

---

## 📊 Current NetBoozt Strategy

### ✅ Committed to Git (Small Assets)
```
docs/assets/logo/
├── LGOLST_WHITE.png        # 45 KB
├── netboozt_icon.png       # 38 KB
├── favicon.ico             # 15 KB
├── favicon-16x16.png       # 2 KB
├── favicon-32x32.png       # 3 KB
├── favicon-48x48.png       # 5 KB
├── favicon-64x64.png       # 8 KB
├── favicon-128x128.png     # 12 KB
└── favicon-256x256.png     # 25 KB
```
**Total: ~153 KB** ✅ Safe for Git

### 🚫 Not Committed (Generated)
```
docs/assets/screenshots/    # Generated by tools/generate_screenshots.py
tools/                      # Development tools only
```

### 📤 VPS Hosted (Future)
- GUI screenshots (when generated)
- Demo videos
- Tutorial content

---

## 🎯 Recommended Workflow

### For Logo/Favicon Changes
```powershell
# 1. Update source
Copy-Item "G:\loust-pro-agency\Presskit\LGOLST_WHITE.png" "docs\assets\logo\"

# 2. Regenerate favicons
python tools\create_favicon.py

# 3. Commit to git
git add docs/assets/logo/
git commit -m "Update LOUST logo and favicons"
git push
```

### For Screenshot Updates
```powershell
# 1. Generate screenshots
python tools\generate_screenshots.py

# 2. Upload to VPS
.\tools\upload_assets.ps1

# 3. Update README with VPS URLs (no git commit needed)
```

---

## 🔐 Security Considerations

### SSH Keys
```bash
# Generate key for VPS
ssh-keygen -t ed25519 -f ~/.ssh/netboozt_vps -C "netboozt-assets"

# Add to VPS
ssh-copy-id -i ~/.ssh/netboozt_vps.pub -p 999 user@vps.loust.pro

# Use in upload script
ssh -i ~/.ssh/netboozt_vps -p 999 user@vps.loust.pro
```

### Permissions
```bash
# On VPS
sudo chown -R www-data:www-data /home/netboozt-assets
sudo chmod -R 755 /home/netboozt-assets
```

---

## 📈 Bandwidth Monitoring

### Check VPS Usage
```bash
# Install vnstat
sudo apt install vnstat

# Monitor bandwidth
vnstat -d   # Daily
vnstat -m   # Monthly
```

### GitHub LFS Quota
```bash
# Check quota
git lfs env | grep -i quota

# View usage
https://github.com/settings/billing
```

---

## ✅ Final Recommendation

**NetBoozt Asset Strategy:**

1. **Logos/Favicons**: ✅ Git (already done)
2. **Screenshots**: 🖥️ VPS hosting (when generated)
3. **Videos**: 🖥️ VPS hosting (future)
4. **Documentation**: ✅ Git (Markdown files)

**Why:**
- Keeps repo lightweight (< 10MB)
- Fast clones for contributors
- Unlimited screenshot/video hosting
- Full control over assets

---

**Last Updated**: November 2025  
**Maintainer**: LOUST (opensource@loust.pro)

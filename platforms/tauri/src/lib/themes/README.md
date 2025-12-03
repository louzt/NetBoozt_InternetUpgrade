# 🎨 NetBoozt Themes

> Sistema de temas y wallpapers para personalizar NetBoozt

## Estructura de Carpetas

```
themes/
├── backgrounds/          # Fondos de pantalla (público - OSS)
│   ├── dark/            # Fondos oscuros
│   ├── light/           # Fondos claros
│   └── abstract/        # Fondos abstractos
├── private/             # Tu carpeta personal (gitignored)
│   └── README.md        # Instrucciones para agregar tus fondos
└── README.md            # Este archivo
```

## 📁 Agregar tus propios fondos

1. Coloca tus imágenes en la carpeta `private/`
2. Soporta: `.jpg`, `.png`, `.webp`, `.gif`
3. Recomendación: **1920x1080** o mayor
4. La carpeta `private/` está en `.gitignore` para proteger tu privacidad

## 🎨 Contribuir fondos al proyecto

¿Tienes un fondo que quieres compartir con la comunidad?

1. Asegúrate de tener los derechos de la imagen o sea de dominio público
2. Coloca la imagen en la carpeta apropiada (`backgrounds/dark/`, etc.)
3. Optimiza el tamaño (WebP recomendado)
4. Agrega un archivo `credits.json` con la atribución:

```json
{
  "filename": "mi-fondo.webp",
  "author": "Tu Nombre",
  "source": "URL de origen",
  "license": "CC0 / MIT / etc"
}
```

## 🎛️ Temas Incluidos

| Tema | Descripción | Preview |
|------|-------------|---------|
| **Default Dark** | Tema oscuro por defecto | 🌙 |
| **Matrix** | Efecto Matrix verde sobre negro | 💚 |
| **Cyber** | Gradiente ciberpunk neón | 💜 |
| **Minimal** | Fondo sólido sin distracciones | ⬛ |

## 📦 Formato de Tema (JSON)

```json
{
  "name": "Mi Tema",
  "version": "1.0.0",
  "author": "Tu Nombre",
  "type": "dark" | "light",
  "background": {
    "type": "solid" | "gradient" | "image",
    "value": "#1a1a1a" | "url('/themes/backgrounds/mi-fondo.webp')"
  },
  "colors": {
    "primary": "#00d4aa",
    "background": "#0a0a0a",
    "card": "#1a1a1a",
    "border": "#2d2d2d",
    "text": "#ffffff",
    "textMuted": "#888888"
  },
  "effects": {
    "glassmorphism": true,
    "blur": 12,
    "cardOpacity": 0.6
  }
}
```

## ⚡ API de Temas

```typescript
// Importar el store de temas
import { currentTheme, setTheme, setWallpaper } from '$lib/stores/themeStore';

// Cambiar tema
setTheme('matrix');

// Establecer wallpaper personalizado
setWallpaper('/themes/private/mi-fondo.jpg');

// Leer tema actual
$currentTheme // { name: 'Matrix', ... }
```

---

**By LOUST** | [www.loust.pro](https://loust.pro)

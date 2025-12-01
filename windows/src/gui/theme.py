"""
NetBoozt - Theme Constants
Colores, estilos y configuración de tema glassmorphism

By LOUST (www.loust.pro)
"""

# ===== GLASSMORPHISM BLACK THEME =====

# Colores principales
PRIMARY = "#00d4aa"  # Verde LOUST
PRIMARY_HOVER = "#00ffcc"
PRIMARY_DARK = "#00a88a"

# Backgrounds - Glassmorphism
BG_MAIN = "#0a0a0a"  # Negro profundo
BG_SIDEBAR = "#0f0f0f"  # Negro sidebar
BG_CARD = "#151515"  # Cards negro con transparencia
BG_CARD_HOVER = "#1a1a1a"  # Hover cards
BG_HOVER = "#1a1a1a"  # Alias for hover state
BG_INPUT = "#1c1c1c"  # Inputs
BG_ACTIVE = "#1e1e1e"  # Elementos activos

# Success/Error backgrounds
SUCCESS_BG = "#0a2a1a"  # Verde oscuro para estados activos
ERROR_BG = "#2a0a0a"  # Rojo oscuro
WARNING_BG = "#2a1a0a"  # Amarillo oscuro

# Borders - Glassmorphism
BORDER_DEFAULT = "#2a2a2a"  # Bordes sutiles
BORDER_HOVER = "#3a3a3a"
BORDER_ACTIVE = PRIMARY
BORDER_GLASS = "rgba(255, 255, 255, 0.05)"  # Efecto vidrio

# Text colors
TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#a0a0a0"
TEXT_DISABLED = "#606060"
TEXT_SUCCESS = "#00ff88"
TEXT_WARNING = "#ffaa00"
TEXT_ERROR = "#ff4444"

# Shadows - Glassmorphism depth
SHADOW_SM = "0 2px 8px rgba(0, 0, 0, 0.3)"
SHADOW_MD = "0 4px 16px rgba(0, 0, 0, 0.4)"
SHADOW_LG = "0 8px 32px rgba(0, 0, 0, 0.5)"
SHADOW_GLOW = f"0 0 20px {PRIMARY}40"  # Glow effect

# Blur effects (CSS-style, for reference)
BLUR_GLASS = "blur(10px)"
BACKDROP_GLASS = "rgba(10, 10, 10, 0.7)"

# ===== ICONOS (Emoji Unicode) =====
ICONS = {
    # Navegación
    'dashboard': '📊',
    'optimization': '⚡',
    'network': '🌐',
    'failover': '🔄',
    'settings': '⚙️',
    'about': 'ℹ️',
    'docs': '📖',
    'github': '🔗',
    'language': '🌍',
    'readme': '📄',
    
    # Estados
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'active': '🟢',
    'inactive': '⚪',
    
    # Acciones
    'refresh': '🔄',
    'apply': '✓',
    'reset': '↺',
    'save': '💾',
    'export': '📤',
    'import': '📥',
    
    # Network
    'ethernet': '🔌',
    'wifi': '📡',
    'dns': '🌐',
    'ping': '📶',
    'speed': '⚡',
    'upload': '⬆️',
    'download': '⬇️',
}

# ===== FONTS =====
FONT_FAMILY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

FONT_SIZE_SMALL = 11
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_TITLE = 16
FONT_SIZE_HEADER = 20
FONT_SIZE_HERO = 24

# ===== SPACING =====
PADDING_SMALL = 5
PADDING_NORMAL = 10
PADDING_LARGE = 15
PADDING_XL = 20

MARGIN_SMALL = 5
MARGIN_NORMAL = 10
MARGIN_LARGE = 15

# ===== DIMENSIONS =====
SIDEBAR_WIDTH = 220
CONTENT_PADDING = 20
CARD_HEIGHT_MIN = 100
BUTTON_HEIGHT = 32
INPUT_HEIGHT = 32

# ===== CORNER RADIUS =====
RADIUS_SMALL = 6
RADIUS_NORMAL = 8
RADIUS_LARGE = 12
RADIUS_BUTTON = 8

# ===== SCROLLBAR =====
SCROLLBAR_WIDTH = 12
SCROLLBAR_COLOR = BG_CARD
SCROLLBAR_HOVER = BG_CARD_HOVER

# ===== LANGUAGE STRINGS =====
LANG = {
    'es': {
        'dashboard': 'Dashboard',
        'optimizations': 'Optimizaciones',
        'network_status': 'Estado de Red',
        'dns_failover': 'Failover DNS',
        'settings': 'Configuración',
        'about': 'Acerca de',
        'documentation': 'Documentación',
        'github': 'GitHub',
        'readme': 'README',
        'language': 'Idioma',
        'apply': 'Aplicar',
        'apply_all': 'Aplicar Todo',
        'refresh': 'Actualizar',
        'reset': 'Restablecer',
        'save': 'Guardar',
        'cancel': 'Cancelar',
        'enabled': 'Activado',
        'disabled': 'Desactivado',
        'active': 'Activo',
        'inactive': 'Inactivo',
        'loading': 'Cargando...',
        'no_data': 'Sin datos',
        'error': 'Error',
        'success': 'Éxito',
        'warning': 'Advertencia',
        'info': 'Información',
    },
    'en': {
        'dashboard': 'Dashboard',
        'optimizations': 'Optimizations',
        'network_status': 'Network Status',
        'dns_failover': 'DNS Failover',
        'settings': 'Settings',
        'about': 'About',
        'documentation': 'Documentation',
        'github': 'GitHub',
        'readme': 'README',
        'language': 'Language',
        'apply': 'Apply',
        'apply_all': 'Apply All',
        'refresh': 'Refresh',
        'reset': 'Reset',
        'save': 'Save',
        'cancel': 'Cancel',
        'enabled': 'Enabled',
        'disabled': 'Disabled',
        'active': 'Active',
        'inactive': 'Inactive',
        'loading': 'Loading...',
        'no_data': 'No data',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Info',
    }
}

# Current language (default: español)
CURRENT_LANG = 'es'

def t(key: str) -> str:
    """Translate key to current language"""
    return LANG.get(CURRENT_LANG, LANG['es']).get(key, key)

def set_language(lang_code: str):
    """Set current language"""
    global CURRENT_LANG
    if lang_code in LANG:
        CURRENT_LANG = lang_code

"""
NetBoozt - GUI Module
Interfaz gráfica moderna con CustomTkinter
"""

from .modern_window import ModernNetBoozt
from .dashboard import NetworkDashboard, RealtimeGraph
from .about_tab import AboutTab
from .readme_tab import ReadmeTab
from .docs_tab import DocsTab
from .github_tab import GitHubTab
from .splash_screen import SplashScreen, show_splash_while_loading
from . import theme

__all__ = [
    'ModernNetBoozt',
    'NetworkDashboard',
    'RealtimeGraph',
    'AboutTab',
    'ReadmeTab',
    'DocsTab',
    'GitHubTab',
    'SplashScreen',
    'show_splash_while_loading',
    'theme'
]
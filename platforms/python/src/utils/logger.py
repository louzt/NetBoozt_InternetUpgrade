"""
NetBoozt - Sistema de Logging Robusto
Registra todos los eventos, errores y debug info con timestamps

By LOUST (www.loust.pro)
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import traceback
import os

# Detectar si estamos en modo frozen (compilado con PyInstaller)
if getattr(sys, 'frozen', False):
    # Estamos en .exe - logs junto al ejecutable
    APP_DIR = Path(sys.executable).parent
else:
    # Modo desarrollo - logs en windows/logs/
    APP_DIR = Path(__file__).parent.parent.parent

# Directorio de logs
LOGS_DIR = APP_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Nombre del archivo de log (por sesión)
SESSION_START = datetime.now()
LOG_FILENAME = f"netboozt_{SESSION_START.strftime('%Y%m%d_%H%M%S')}.log"
LOG_PATH = LOGS_DIR / LOG_FILENAME

# Configurar logger
logger = logging.getLogger("NetBoozt")
logger.setLevel(logging.DEBUG)

# Formato detallado
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler para archivo
try:
    file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as e:
    # Si no se puede crear el archivo de log, al menos registrarlo en consola
    # Cannot use logger here as it's being initialized
    pass

# Handler para consola (solo errores críticos)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Log de inicio de sesión
logger.info("="*80)
logger.info(f"NetBoozt Session Started - {SESSION_START.strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Log file: {LOG_PATH}")
logger.info(f"App directory: {APP_DIR}")
logger.info(f"Frozen mode: {getattr(sys, 'frozen', False)}")
logger.info(f"Python: {sys.version}")
logger.info(f"Platform: {sys.platform}")
logger.info("="*80)


def log_info(message: str, module: str = None):
    """Log información general"""
    if module:
        logger.info(f"[{module}] {message}")
    else:
        logger.info(message)


def log_debug(message: str, module: str = None):
    """Log debug info"""
    if module:
        logger.debug(f"[{module}] {message}")
    else:
        logger.debug(message)


def log_warning(message: str, module: str = None):
    """Log advertencias"""
    if module:
        logger.warning(f"[{module}] {message}")
    else:
        logger.warning(message)


def log_error(message: str, exception: Exception = None, module: str = None):
    """Log errores con traceback completo"""
    prefix = f"[{module}] " if module else ""
    
    if exception:
        logger.error(f"{prefix}{message}")
        logger.error(f"Exception type: {type(exception).__name__}")
        logger.error(f"Exception message: {str(exception)}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
    else:
        logger.error(f"{prefix}{message}")
        # Capturar traceback actual si existe
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            logger.error("Current exception info:")
            logger.error(traceback.format_exc())


def log_critical(message: str, exception: Exception = None, module: str = None):
    """Log errores críticos que detienen la aplicación"""
    prefix = f"[{module}] " if module else ""
    
    logger.critical(f"{prefix}CRITICAL: {message}")
    if exception:
        logger.critical(f"Exception type: {type(exception).__name__}")
        logger.critical(f"Exception message: {str(exception)}")
        logger.critical("Full traceback:")
        logger.critical(traceback.format_exc())


def log_exception(exception: Exception, context: str = None):
    """Log excepción con contexto completo"""
    if context:
        logger.exception(f"Exception in {context}: {str(exception)}")
    else:
        logger.exception(f"Exception: {str(exception)}")


def get_latest_log_path() -> Path:
    """Obtener path del archivo de log más reciente"""
    return LOG_PATH


def get_all_logs() -> list[Path]:
    """Obtener lista de todos los archivos de log"""
    if not LOGS_DIR.exists():
        return []
    return sorted(LOGS_DIR.glob("netboozt_*.log"), reverse=True)


def clean_old_logs(keep_latest: int = 10):
    """Limpiar logs antiguos, manteniendo solo los más recientes"""
    all_logs = get_all_logs()
    if len(all_logs) > keep_latest:
        for old_log in all_logs[keep_latest:]:
            try:
                old_log.unlink()
                log_info(f"Deleted old log: {old_log.name}")
            except Exception as e:
                log_warning(f"Could not delete old log {old_log.name}: {e}")


# Auto-limpiar logs viejos al inicio
try:
    clean_old_logs(keep_latest=10)
except Exception as e:
    logger.warning(f"Could not clean old logs: {e}")


# Context manager para log de secciones
class LogSection:
    """Context manager para loggear secciones de código"""
    
    def __init__(self, section_name: str, module: str = None):
        self.section_name = section_name
        self.module = module
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        log_info(f">>> Starting: {self.section_name}", self.module)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is not None:
            log_error(
                f"<<< FAILED: {self.section_name} (after {duration:.2f}s)",
                exception=exc_val,
                module=self.module
            )
            return False  # Re-raise exception
        else:
            log_info(f"<<< Completed: {self.section_name} ({duration:.2f}s)", self.module)
            return True


# Example usage
if __name__ == "__main__":
    log_info("Testing logger system")
    log_debug("Debug message")
    log_warning("Warning message")
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error("Caught test error", e)
    
    log_info(f"Log saved to: {LOG_PATH}")

"""
NetBoozt - Storage Manager
Sistema ligero de persistencia de datos sin SQLite

Usa TinyDB (JSON puro, ligero, sin dependencias SQL)
Perfecto para:
- Historial de pruebas de red
- Configuraciones de usuario
- Logs de optimizaciones aplicadas
- Métricas en tiempo real

By LOUST (www.loust.pro)
"""

from tinydb import TinyDB, Query
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json


class NetBooztStorage:
    """Gestor de almacenamiento local para NetBoozt"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Inicializar almacenamiento
        
        Args:
            db_path: Ruta personalizada para la DB. 
                     Por defecto: %APPDATA%/NetBoozt/data.json
        """
        if db_path is None:
            appdata = Path.home() / "AppData" / "Roaming" / "NetBoozt"
            appdata.mkdir(parents=True, exist_ok=True)
            db_path = appdata / "netboozt_data.json"
        
        self.db_path = db_path
        self.db = TinyDB(db_path, indent=2, ensure_ascii=False)
        
        # Tablas separadas
        self.tests = self.db.table('network_tests')
        self.optimizations = self.db.table('optimizations')
        self.settings = self.db.table('settings')
        self.metrics = self.db.table('metrics')
    
    def __del__(self):
        """Cleanup al destruir el objeto"""
        try:
            self.close()
        except Exception:
            # Ignore errors during cleanup
            pass
    
    # ==================== Tests de Red ====================
    
    def save_network_test(self, test_data: Dict) -> int:
        """
        Guardar resultado de prueba de red
        
        Args:
            test_data: {
                'timestamp': str,
                'adapter': str,
                'download_mbps': float,
                'upload_mbps': float,
                'latency_ms': float,
                'jitter_ms': float,
                'packet_loss': float,
                'mtu': int,
                'dns_servers': List[str]
            }
        
        Returns:
            ID del test guardado
        """
        test_data['timestamp'] = datetime.now().isoformat()
        return self.tests.insert(test_data)
    
    def get_recent_tests(self, limit: int = 10) -> List[Dict]:
        """Obtener tests recientes"""
        all_tests = self.tests.all()
        # Ordenar por timestamp desc
        sorted_tests = sorted(
            all_tests, 
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        return sorted_tests[:limit]
    
    def get_tests_by_date_range(self, start: datetime, end: datetime) -> List[Dict]:
        """Obtener tests en rango de fechas"""
        Test = Query()
        return self.tests.search(
            (Test.timestamp >= start.isoformat()) & 
            (Test.timestamp <= end.isoformat())
        )
    
    def get_test_stats(self) -> Dict:
        """Estadísticas de todos los tests"""
        all_tests = self.tests.all()
        
        if not all_tests:
            return {
                'total_tests': 0,
                'avg_download': 0,
                'avg_upload': 0,
                'avg_latency': 0,
                'best_download': 0,
                'worst_latency': 999
            }
        
        downloads = [t.get('download_mbps', 0) for t in all_tests]
        uploads = [t.get('upload_mbps', 0) for t in all_tests]
        latencies = [t.get('latency_ms', 0) for t in all_tests]
        
        return {
            'total_tests': len(all_tests),
            'avg_download': sum(downloads) / len(downloads),
            'avg_upload': sum(uploads) / len(uploads),
            'avg_latency': sum(latencies) / len(latencies),
            'best_download': max(downloads),
            'worst_latency': max(latencies)
        }
    
    # ==================== Optimizaciones ====================
    
    def save_optimization(self, opt_data: Dict) -> int:
        """
        Guardar optimización aplicada
        
        Args:
            opt_data: {
                'name': str,
                'category': str,
                'enabled': bool,
                'applied_at': str,
                'success': bool,
                'error': Optional[str]
            }
        """
        opt_data['applied_at'] = datetime.now().isoformat()
        return self.optimizations.insert(opt_data)
    
    def get_active_optimizations(self) -> List[Dict]:
        """Obtener optimizaciones actualmente activas"""
        Opt = Query()
        return self.optimizations.search(Opt.enabled == True)
    
    def get_optimization_history(self, name: str) -> List[Dict]:
        """Historial de una optimización específica"""
        Opt = Query()
        return self.optimizations.search(Opt.name == name)
    
    def toggle_optimization(self, name: str, enabled: bool):
        """Marcar optimización como activada/desactivada"""
        Opt = Query()
        self.optimizations.update(
            {'enabled': enabled, 'last_updated': datetime.now().isoformat()},
            Opt.name == name
        )
    
    def save_optimization_state(self, state_dict: Dict[str, bool]):
        """
        Guardar estado completo de optimizaciones (cache local)
        
        Args:
            state_dict: {'hystart': True, 'prr': False, ...}
        """
        data = {
            'state': state_dict,
            'detected_at': datetime.now().isoformat()
        }
        
        # Usar tabla de settings con key especial
        self.save_setting('optimization_state_cache', data)
    
    def load_optimization_state(self) -> Optional[Dict[str, bool]]:
        """
        Cargar estado cacheado de optimizaciones
        
        Returns:
            Dict con estado o None si no hay cache
        """
        cache = self.get_setting('optimization_state_cache')
        
        if cache and isinstance(cache, dict):
            # Verificar que el cache no sea muy viejo (max 1 hora)
            detected_at = cache.get('detected_at')
            if detected_at:
                try:
                    from datetime import datetime, timedelta
                    cached_time = datetime.fromisoformat(detected_at)
                    age = datetime.now() - cached_time
                    
                    if age < timedelta(hours=1):
                        return cache.get('state', {})
                except:
                    pass
        
        return None
    
    # ==================== Configuración ====================
    
    def save_setting(self, key: str, value):
        """Guardar configuración"""
        Setting = Query()
        existing = self.settings.search(Setting.key == key)
        
        data = {
            'key': key,
            'value': value,
            'updated_at': datetime.now().isoformat()
        }
        
        if existing:
            self.settings.update(data, Setting.key == key)
        else:
            self.settings.insert(data)
    
    def get_setting(self, key: str, default=None):
        """Obtener configuración"""
        Setting = Query()
        result = self.settings.search(Setting.key == key)
        
        if result:
            return result[0].get('value', default)
        return default
    
    def get_all_settings(self) -> Dict:
        """Todas las configuraciones como dict"""
        all_settings = self.settings.all()
        return {s['key']: s['value'] for s in all_settings}
    
    # ==================== Métricas Real-Time ====================
    
    def save_metric(self, metric_data: Dict) -> int:
        """
        Guardar métrica de red en tiempo real
        
        Args:
            metric_data: {
                'timestamp': str,
                'adapter': str,
                'bytes_sent': int,
                'bytes_recv': int,
                'packets_sent': int,
                'packets_recv': int,
                'errors_in': int,
                'errors_out': int,
                'drops_in': int,
                'drops_out': int
            }
        """
        metric_data['timestamp'] = datetime.now().isoformat()
        
        # Guardar
        metric_id = self.metrics.insert(metric_data)
        
        # Limpiar métricas viejas (solo mantener últimas 1000)
        all_metrics = self.metrics.all()
        if len(all_metrics) > 1000:
            # Eliminar las más antiguas
            sorted_metrics = sorted(
                all_metrics,
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            to_delete = sorted_metrics[1000:]
            for metric in to_delete:
                self.metrics.remove(doc_ids=[metric.doc_id])
        
        return metric_id
    
    def get_recent_metrics(self, limit: int = 100) -> List[Dict]:
        """Obtener métricas recientes para gráficas"""
        all_metrics = self.metrics.all()
        sorted_metrics = sorted(
            all_metrics,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
        return sorted_metrics[:limit]
    
    # ==================== Utilidades ====================
    
    def export_to_json(self, filepath: Path):
        """Exportar toda la DB a JSON"""
        data = {
            'tests': self.tests.all(),
            'optimizations': self.optimizations.all(),
            'settings': self.settings.all(),
            'metrics': self.get_recent_metrics(1000),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_from_json(self, filepath: Path):
        """Importar datos desde JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Insertar datos
        if 'tests' in data:
            self.tests.insert_multiple(data['tests'])
        if 'optimizations' in data:
            self.optimizations.insert_multiple(data['optimizations'])
        if 'settings' in data:
            for setting in data['settings']:
                self.save_setting(setting['key'], setting['value'])
        if 'metrics' in data:
            self.metrics.insert_multiple(data['metrics'])
    
    def clear_old_data(self, days: int = 30):
        """Eliminar datos más antiguos que X días"""
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        Test = Query()
        self.tests.remove(Test.timestamp < cutoff)
        self.metrics.remove(Test.timestamp < cutoff)
    
    def get_db_stats(self) -> Dict:
        """Estadísticas de la base de datos"""
        return {
            'db_path': str(self.db_path),
            'db_size_bytes': self.db_path.stat().st_size if self.db_path.exists() else 0,
            'total_tests': len(self.tests),
            'total_optimizations': len(self.optimizations),
            'total_settings': len(self.settings),
            'total_metrics': len(self.metrics)
        }
    
    def close(self):
        """Cerrar DB"""
        self.db.close()


# Singleton global
_storage_instance = None

def get_storage() -> NetBooztStorage:
    """Obtener instancia única del storage"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = NetBooztStorage()
    return _storage_instance

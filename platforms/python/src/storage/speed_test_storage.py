"""
NetBoozt - Speed Test Storage con Limpieza Inteligente
Estrategia 3-2-1 para evitar saturación de DB

By LOUST (www.loust.pro)
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics

try:
    from ..storage.db_manager import NetBooztStorage
    from ..utils.logger import log_info, log_warning
except ImportError:
    NetBooztStorage = None
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")


@dataclass
class SpeedTestResult:
    """Resultado de prueba de velocidad"""
    timestamp: datetime
    download_mbps: float
    upload_mbps: float
    latency_ms: float
    jitter_ms: float
    packet_loss: float
    adapter: str
    server: str
    test_duration_s: float


class SpeedTestStorage:
    """
    Almacenamiento inteligente de speed tests
    
    Estrategia 3-2-1:
    - Últimas 24h: TODO (granularidad fina)
    - 1-7 días: 1 por hora (promedio)
    - 8-30 días: 1 por día (promedio)
    - 30+ días: 1 por semana (promedio)
    """
    
    def __init__(self, storage: 'NetBooztStorage'):
        self.storage = storage
    
    def save_test(self, result: SpeedTestResult) -> int:
        """Guardar resultado y aplicar cleanup"""
        # Convertir a dict
        data = asdict(result)
        data['timestamp'] = result.timestamp.isoformat()
        
        # Guardar
        test_id = self.storage.save_network_test(data)
        log_info(f"Speed test guardado: {result.download_mbps:.1f}↓ {result.upload_mbps:.1f}↑ Mbps")
        
        # Cleanup inteligente
        self._intelligent_cleanup()
        
        return test_id
    
    def _intelligent_cleanup(self):
        """Limpieza inteligente según estrategia 3-2-1"""
        try:
            now = datetime.now()
            all_tests = self.storage.tests.all()
            
            if not all_tests:
                return
            
            # Parsear timestamps
            for test in all_tests:
                if isinstance(test.get('timestamp'), str):
                    test['timestamp'] = datetime.fromisoformat(test['timestamp'])
            
            # Separar por rangos
            last_24h = []
            last_week = []
            last_month = []
            older = []
            
            for test in all_tests:
                ts = test['timestamp']
                age = now - ts
                
                if age < timedelta(hours=24):
                    last_24h.append(test)
                elif age < timedelta(days=7):
                    last_week.append(test)
                elif age < timedelta(days=30):
                    last_month.append(test)
                else:
                    older.append(test)
            
            # Últimas 24h: Mantener TODO
            keep_ids = {t.doc_id for t in last_24h}
            
            # 1-7 días: 1 por hora (agrupar y promediar)
            if last_week:
                hourly = self._aggregate_by_hour(last_week)
                keep_ids.update(t.doc_id for t in hourly)
            
            # 8-30 días: 1 por día
            if last_month:
                daily = self._aggregate_by_day(last_month)
                keep_ids.update(t.doc_id for t in daily)
            
            # 30+ días: 1 por semana
            if older:
                weekly = self._aggregate_by_week(older)
                keep_ids.update(t.doc_id for t in weekly)
            
            # Eliminar lo que NO está en keep_ids
            all_ids = {t.doc_id for t in all_tests}
            to_delete = all_ids - keep_ids
            
            if to_delete:
                for doc_id in to_delete:
                    self.storage.tests.remove(doc_ids=[doc_id])
                
                log_info(f"Cleanup: {len(to_delete)} tests antiguos eliminados, {len(keep_ids)} mantenidos")
        
        except Exception as e:
            log_warning(f"Error en cleanup: {e}")
    
    def _aggregate_by_hour(self, tests: List[dict]) -> List[dict]:
        """Agrupar por hora y seleccionar representativo"""
        by_hour = {}
        
        for test in tests:
            hour_key = test['timestamp'].replace(minute=0, second=0, microsecond=0)
            
            if hour_key not in by_hour:
                by_hour[hour_key] = []
            
            by_hour[hour_key].append(test)
        
        # Seleccionar 1 por hora (el más cercano al minuto 30)
        selected = []
        for hour, group in by_hour.items():
            # Buscar el más cercano a :30
            target = hour.replace(minute=30)
            closest = min(group, key=lambda t: abs((t['timestamp'] - target).total_seconds()))
            selected.append(closest)
        
        return selected
    
    def _aggregate_by_day(self, tests: List[dict]) -> List[dict]:
        """Agrupar por día y seleccionar representativo"""
        by_day = {}
        
        for test in tests:
            day_key = test['timestamp'].date()
            
            if day_key not in by_day:
                by_day[day_key] = []
            
            by_day[day_key].append(test)
        
        # Seleccionar 1 por día (el del mediodía)
        selected = []
        for day, group in by_day.items():
            noon = datetime.combine(day, datetime.min.time()).replace(hour=12)
            closest = min(group, key=lambda t: abs((t['timestamp'] - noon).total_seconds()))
            selected.append(closest)
        
        return selected
    
    def _aggregate_by_week(self, tests: List[dict]) -> List[dict]:
        """Agrupar por semana y seleccionar representativo"""
        by_week = {}
        
        for test in tests:
            # ISO week number
            week_key = (test['timestamp'].isocalendar()[0], test['timestamp'].isocalendar()[1])
            
            if week_key not in by_week:
                by_week[week_key] = []
            
            by_week[week_key].append(test)
        
        # Seleccionar 1 por semana (miércoles mediodía si existe)
        selected = []
        for week, group in by_week.items():
            # Buscar miércoles (weekday 2)
            wednesdays = [t for t in group if t['timestamp'].weekday() == 2]
            
            if wednesdays:
                closest = min(wednesdays, key=lambda t: abs(t['timestamp'].hour - 12))
            else:
                # Si no hay miércoles, tomar el del medio
                closest = group[len(group) // 2]
            
            selected.append(closest)
        
        return selected
    
    def get_recent(self, hours: int = 24) -> List[Dict]:
        """Obtener tests recientes"""
        cutoff = datetime.now() - timedelta(hours=hours)
        all_tests = self.storage.get_recent_tests(limit=1000)
        
        recent = []
        for test in all_tests:
            ts = datetime.fromisoformat(test['timestamp']) if isinstance(test['timestamp'], str) else test['timestamp']
            if ts >= cutoff:
                recent.append(test)
        
        return recent
    
    def get_stats(self, days: int = 7) -> Dict:
        """Obtener estadísticas de período"""
        cutoff = datetime.now() - timedelta(days=days)
        all_tests = self.storage.get_recent_tests(limit=1000)
        
        period_tests = []
        for test in all_tests:
            ts = datetime.fromisoformat(test['timestamp']) if isinstance(test['timestamp'], str) else test['timestamp']
            if ts >= cutoff:
                period_tests.append(test)
        
        if not period_tests:
            return {
                'count': 0,
                'avg_download': 0,
                'avg_upload': 0,
                'avg_latency': 0,
                'max_download': 0,
                'min_download': 0
            }
        
        downloads = [t['download_mbps'] for t in period_tests]
        uploads = [t['upload_mbps'] for t in period_tests]
        latencies = [t['latency_ms'] for t in period_tests]
        
        return {
            'count': len(period_tests),
            'avg_download': statistics.mean(downloads),
            'avg_upload': statistics.mean(uploads),
            'avg_latency': statistics.mean(latencies),
            'max_download': max(downloads),
            'min_download': min(downloads),
            'median_download': statistics.median(downloads)
        }


if __name__ == "__main__":
    print("SpeedTestStorage - Test Mode")
    print("Requiere NetBooztStorage para funcionar")

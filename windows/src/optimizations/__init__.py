"""
NetBoozt - Optimizations Module
Detección y aplicación de optimizaciones TCP/IP
"""

from .detection import OptimizationDetector, OptimizationState, detect_optimizations

__all__ = ['OptimizationDetector', 'OptimizationState', 'detect_optimizations']

"""
Utilidad de cache simple para health checks con TTL
"""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class HealthCheckCache:
    """
    Cache simple para health checks con Time-To-Live (TTL).
    Evita llamadas repetidas a servicios en períodos cortos.
    """

    def __init__(self, ttl_seconds: int = 5):
        """
        Inicializar cache con TTL configurable

        Args:
            ttl_seconds: Tiempo de vida del cache en segundos (default: 5)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, dict[str, Any]] = {}
        self._timestamps: dict[str, float] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        """
        Obtener valor del cache si existe y no ha expirado

        Args:
            key: Clave del cache

        Returns:
            Valor cacheado o None si no existe o expiró
        """
        if key not in self._cache:
            return None

        # Verificar si ha expirado
        age = time.time() - self._timestamps[key]
        if age > self.ttl_seconds:
            # Expiró, eliminar del cache
            del self._cache[key]
            del self._timestamps[key]
            return None

        logger.debug(f"Cache hit for '{key}' (age: {age:.2f}s)")
        return self._cache[key]

    def set(self, key: str, value: dict[str, Any]):
        """
        Guardar valor en el cache

        Args:
            key: Clave del cache
            value: Valor a cachear
        """
        self._cache[key] = value
        self._timestamps[key] = time.time()
        logger.debug(f"Cache set for '{key}' (TTL: {self.ttl_seconds}s)")

    def clear(self, key: str | None = None):
        """
        Limpiar cache (específico o completo)

        Args:
            key: Clave específica a limpiar, o None para limpiar todo
        """
        if key:
            if key in self._cache:
                del self._cache[key]
                del self._timestamps[key]
                logger.debug(f"Cache cleared for '{key}'")
        else:
            self._cache.clear()
            self._timestamps.clear()
            logger.debug("All cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """Obtener estadísticas del cache"""
        current_time = time.time()
        active_entries = sum(
            1
            for key, timestamp in self._timestamps.items()
            if (current_time - timestamp) <= self.ttl_seconds
        )

        return {
            "total_entries": len(self._cache),
            "active_entries": active_entries,
            "ttl_seconds": self.ttl_seconds,
            "cache_keys": list(self._cache.keys()),
        }


# Global cache instance for health checks (5 seconds TTL)
health_check_cache = HealthCheckCache(ttl_seconds=5)


def cached_health_check(service_name: str):
    """
    Decorator para cachear resultados de health checks

    Args:
        service_name: Nombre del servicio para usar como clave de cache
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Intentar obtener del cache
            cached_result = health_check_cache.get(service_name)
            if cached_result is not None:
                return cached_result

            # No en cache o expirado, ejecutar función
            result = func(*args, **kwargs)

            # Save en cache
            health_check_cache.set(service_name, result)

            return result

        return wrapper

    return decorator

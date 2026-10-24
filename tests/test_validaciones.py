
from datetime import datetime, timezone

import pytest

from src.ingestion.validaciones import validar_medicion


def test_medicion_correcta():
    """Comprueba que una medición válida no genera errores."""

    validar_medicion(
        zona="M-30 Madrid",
        velocidad_media_kmh=62.5,
        fecha_medicion=datetime.now(timezone.utc)
    )


def test_zona_vacia():
    """Comprueba que una zona vacía se rechaza."""

    with pytest.raises(ValueError, match="zona"):
        validar_medicion(
            zona="",
            velocidad_media_kmh=62.5,
            fecha_medicion=datetime.now(timezone.utc)
        )


def test_velocidad_negativa():
    """Comprueba que una velocidad negativa se rechaza."""

    with pytest.raises(ValueError, match="velocidad"):
        validar_medicion(
            zona="M-30 Madrid",
            velocidad_media_kmh=-10,
            fecha_medicion=datetime.now(timezone.utc)
        )


def test_fecha_sin_zona_horaria():
    """Comprueba que una fecha sin zona horaria se rechaza."""

    with pytest.raises(ValueError, match="zona horaria"):
        validar_medicion(
            zona="M-30 Madrid",
            velocidad_media_kmh=62.5,
            fecha_medicion=datetime(2026, 10, 24, 22, 30)
        )

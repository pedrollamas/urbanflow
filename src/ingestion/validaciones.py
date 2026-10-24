
from datetime import datetime


def validar_medicion(zona, velocidad_media_kmh, fecha_medicion):
    """Valida los datos de una medición de tráfico."""

    if not isinstance(zona, str) or not zona.strip():
        raise ValueError("La zona debe ser un texto no vacío")

    if isinstance(velocidad_media_kmh, bool) or not isinstance(
        velocidad_media_kmh, (int, float)
    ):
        raise ValueError("La velocidad debe ser numérica")

    if not 0 <= velocidad_media_kmh <= 200:
        raise ValueError("La velocidad debe estar entre 0 y 200 km/h")

    if not isinstance(fecha_medicion, datetime):
        raise ValueError("La fecha debe ser un objeto datetime")

    if fecha_medicion.tzinfo is None or fecha_medicion.utcoffset() is None:
        raise ValueError("La fecha debe incluir zona horaria")

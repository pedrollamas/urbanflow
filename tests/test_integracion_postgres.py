
import os
from datetime import datetime, timezone
from decimal import Decimal

import psycopg
import pytest


@pytest.fixture
def conexion_pruebas():
    """Abre y cierra una conexión con la base de pruebas."""

    conexion = psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname="urbanflow_test",
        user=os.environ.get("POSTGRES_USER", "urbanflow"),
        password=os.environ["POSTGRES_TEST_PASSWORD"]
    )

    try:
        yield conexion
    finally:
        conexion.close()


def test_upsert_medicion(conexion_pruebas):
    """Comprueba inserción, idempotencia y actualización."""

    zona = "TEST-M30"
    fecha = datetime(2026, 10, 24, 22, 30, tzinfo=timezone.utc)

    with conexion_pruebas.cursor() as cursor:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mediciones_trafico (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                zona VARCHAR(100) NOT NULL,
                velocidad_media_kmh NUMERIC(6, 2) NOT NULL,
                fecha_medicion TIMESTAMPTZ NOT NULL,
                CONSTRAINT uq_mediciones_zona_fecha
                    UNIQUE (zona, fecha_medicion)
            )
        """)

        cursor.execute("""
            INSERT INTO mediciones_trafico
                (zona, velocidad_media_kmh, fecha_medicion)
            VALUES (%s, %s, %s)
            ON CONFLICT (zona, fecha_medicion)
            DO UPDATE SET
                velocidad_media_kmh = EXCLUDED.velocidad_media_kmh
        """, (zona, 62.5, fecha))

        # Repetimos la misma medición
        cursor.execute("""
            INSERT INTO mediciones_trafico
                (zona, velocidad_media_kmh, fecha_medicion)
            VALUES (%s, %s, %s)
            ON CONFLICT (zona, fecha_medicion)
            DO UPDATE SET
                velocidad_media_kmh = EXCLUDED.velocidad_media_kmh
        """, (zona, 62.5, fecha))

        # Corregimos la velocidad
        cursor.execute("""
            INSERT INTO mediciones_trafico
                (zona, velocidad_media_kmh, fecha_medicion)
            VALUES (%s, %s, %s)
            ON CONFLICT (zona, fecha_medicion)
            DO UPDATE SET
                velocidad_media_kmh = EXCLUDED.velocidad_media_kmh
        """, (zona, 48.3, fecha))

        cursor.execute("""
            SELECT COUNT(*), MAX(velocidad_media_kmh)
            FROM mediciones_trafico
            WHERE zona = %s AND fecha_medicion = %s
        """, (zona, fecha))

        cantidad, velocidad = cursor.fetchone()

        assert cantidad == 1
        assert velocidad == Decimal("48.30")

    # Deshacemos todos los cambios del test
    conexion_pruebas.rollback()

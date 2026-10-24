import os
from datetime import datetime, timezone

import psycopg


def obtener_conexion():
    """Crea una conexión con PostgreSQL."""
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )


def guardar_medicion():
    """Crea la tabla e inserta una medición de tráfico."""

    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mediciones_trafico (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    zona VARCHAR(100) NOT NULL,
                    velocidad_media_kmh NUMERIC(6, 2) NOT NULL,
                    fecha_medicion TIMESTAMPTZ NOT NULL
                )
            """)

            cursor.execute("""
                INSERT INTO mediciones_trafico (
                    zona,
                    velocidad_media_kmh,
                    fecha_medicion
                )
                VALUES (%s, %s, %s)
            """, (
                "M-30 Madrid",
                62.5,
                datetime.now(timezone.utc)
            ))

        conexion.commit()

    print("Medición de tráfico guardada correctamente.")


if __name__ == "__main__":
    guardar_medicion()
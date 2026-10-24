
import os
import logging
import time
from datetime import datetime, timezone

import psycopg

from validaciones import validar_medicion


# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def obtener_conexion():
    """Crea una conexión con PostgreSQL."""

    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )


def guardar_medicion(zona, velocidad_media_kmh, fecha_medicion):
    """Valida e inserta o actualiza una medición de tráfico."""

    inicio = time.perf_counter()

    logger.info("Inicio de ingesta: zona=%s", zona)

    try:
        # 1. Validación de los datos
        validar_medicion(
            zona=zona,
            velocidad_media_kmh=velocidad_media_kmh,
            fecha_medicion=fecha_medicion
        )

        logger.info("Validación de datos superada")

        # 2. Conexión a PostgreSQL
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:

                # 3. Crear la tabla si no existe
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

                # 4. Insertar o actualizar la medición
                cursor.execute("""
                    INSERT INTO mediciones_trafico (
                        zona,
                        velocidad_media_kmh,
                        fecha_medicion
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (zona, fecha_medicion)
                    DO UPDATE SET
                        velocidad_media_kmh = EXCLUDED.velocidad_media_kmh
                    WHERE mediciones_trafico.velocidad_media_kmh
                          IS DISTINCT FROM EXCLUDED.velocidad_media_kmh
                """, (
                    zona,
                    velocidad_media_kmh,
                    fecha_medicion
                ))

        logger.info(
            "Medición procesada correctamente: zona=%s",
            zona
        )

    except ValueError as error:
        logger.error(
            "Medición rechazada: zona=%s | motivo=%s",
            zona,
            error
        )
        raise

    except psycopg.Error:
        logger.exception(
            "Error de PostgreSQL al procesar zona=%s",
            zona
        )
        raise

    finally:
        duracion = time.perf_counter() - inicio

        logger.info(
            "Duración de la ejecución: %.3f segundos",
            duracion
        )


if __name__ == "__main__":

    fecha_medicion = datetime(
        2026, 10, 24, 22, 30, 0,
        tzinfo=timezone.utc
    )

    guardar_medicion(
        zona="M-30 Madrid",
        velocidad_media_kmh=48.0,
        fecha_medicion=fecha_medicion
    )

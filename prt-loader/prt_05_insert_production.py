# 05 - Insert
# Copiar datos desde la tabla staging a la tabla de producción
# y limpiar la tabla staging.

import argparse
import os

import pymysql
from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Configuración por defecto
# ---------------------------------------------------------------------------

DEFAULT_SOURCE_TABLE = os.environ["TABLE_NAME_TMP"]
DEFAULT_TARGET_TABLE = os.environ["TABLE_NAME"]

DEFAULT_SSH_ALIAS = os.environ["SSH_ALIAS"]

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]

# ---------------------------------------------------------------------------
# Conexión a MySQL
# ---------------------------------------------------------------------------

def get_connection():
    """Crear una conexión a MySQL usando las variables de entorno."""

    conn = pymysql.connect(
        host = DB_HOST,
        port = DB_PORT,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME,
        autocommit = False,
        charset = "utf8mb4"
    )
    return conn

# ---------------------------------------------------------------------------
# Traspaso de staging a producción
# ---------------------------------------------------------------------------

def load(source_table, target_table):
    """
    Copiar los datos desde la tabla staging a la tabla de producción
    y posteriormente limpiar la tabla staging.
    """

    conn = get_connection()
    try:
        with conn.cursor() as cur:

            # ----------------------------------------------------------------
            # 1. Copiar datos desde staging a producción
            # ----------------------------------------------------------------

            sql_insert = f"""
                INSERT INTO {target_table} (
                    COD_PRT,
                    PPU,
                    COD_VEHICULO,
                    COD_COMBUSTIBLE,
                    COD_SERVICIO,
                    MARCA,
                    MODELO,
                    ANO_FABRICACION,
                    NUM_MOTOR,
                    NUM_CHASIS,
                    VIN,
                    KILOMETRAJE,
                    NUM_CERTIFICADO,
                    FEC_REVISION,
                    FEC_VENCIMIENTO,
                    HORA_INI,
                    HORA_FIN,
                    RESULTADO_CRT,
                    FEC_VENCIMIENTO_GASES,
                    RESULTADO_CRT_GASES,
                    IDENTIFICACION,
                    VISUAL,
                    LUCES,
                    ALINEACION,
                    FRENOS,
                    HOLGURAS,
                    SUSPENSION,
                    GASES,
                    OPACIDAD
                )
                SELECT
                    COD_PRT,
                    PPU,
                    COD_VEHICULO,
                    COD_COMBUSTIBLE,
                    COD_SERVICIO,
                    MARCA,
                    MODELO,
                    ANO_FABRICACION,
                    NUM_MOTOR,
                    NUM_CHASIS,
                    VIN,
                    KILOMETRAJE,
                    NUM_CERTIFICADO,
                    FEC_REVISION,
                    FEC_VENCIMIENTO,
                    HORA_INI,
                    HORA_FIN,
                    RESULTADO_CRT,
                    FEC_VENCIMIENTO_GASES,
                    RESULTADO_CRT_GASES,
                    IDENTIFICACION,
                    VISUAL,
                    LUCES,
                    ALINEACION,
                    FRENOS,
                    HOLGURAS,
                    SUSPENSION,
                    GASES,
                    OPACIDAD
                FROM {source_table};
            """

            cur.execute(sql_insert)

        conn.commit()

        print("[OK] Datos traspasados a producción.")

        # ----------------------------------------------------------------
        # 2. Limpiar tabla staging
        # ----------------------------------------------------------------

        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {source_table};")
        conn.commit()

        print("[OK] Tabla staging limpiada.")
        print("[OK] Proceso de carga terminado.")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error durante la carga: {e}")
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Traspasa los datos desde una tabla staging a la tabla de producción y limpia staging."
    )

    parser.add_argument(
        "--source-table",
        default=DEFAULT_SOURCE_TABLE,
        help="Tabla staging de origen.",
    )

    parser.add_argument(
        "--target-table",
        default=DEFAULT_TARGET_TABLE,
        help="Tabla de producción de destino.",
    )

    args = parser.parse_args()

    print(
        f"Origen: {args.source_table}\n"
        f"Destino: {args.target_table}\n"
    )

    load(source_table=args.source_table, target_table=args.target_table)

if __name__ == "__main__":
    main()

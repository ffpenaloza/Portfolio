# 04 - Upload
# Cargar archivos CSV procesados a MySQL mediante SSH + LOAD DATA INFILE

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Configuración por defecto
# ---------------------------------------------------------------------------

DEFAULT_INPUT_FOLDER = Path("D:/ferna/Downloads/DL - Calistoweb/PRT/extracted_cleaned")
DEFAULT_MOVE_FOLDER = Path("D:/ferna/Downloads/DL - Calistoweb/PRT/extracted_cleaned/uploaded")
DEFAULT_SSH_ALIAS = os.environ["SSH_ALIAS"]

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]

MONTH_NAMES = [
    "ene",
    "feb",
    "mar",
    "abr",
    "may",
    "jun",
    "jul",
    "ago",
    "sep",
    "oct",
    "nov",
    "dic",
]

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
# Obtener año y mes desde el nombre del archivo
# ---------------------------------------------------------------------------

def extract_year_month(filename):
    """
    Extraer año y mes del nombre del archivo.

    Ejemplo:
        SGPRT_RB_ago-2026.csv

    Retorna:
        (2026, 8)
    """

    try:
        match = re.search(r"_([a-zA-Z]{3})-(\d{4})", filename)
        if match:
            month_str, year = match.groups()
            year = int(year)
            month = MONTH_NAMES.index(month_str.lower()) + 1
            return year, month

        return 9999, 12
    except (ValueError, AttributeError):
        return 9999, 12

# ---------------------------------------------------------------------------
# Cargar CSV mediante SSH + LOAD DATA INFILE
# ---------------------------------------------------------------------------

def import_csv_via_ssh_load_infile(local_csv_path, table, ssh_alias=DEFAULT_SSH_ALIAS):
    """
    Copiar un CSV al servidor mediante SCP y cargarlo en MySQL
    utilizando LOAD DATA INFILE.
    """

    local_csv = Path(local_csv_path)
    remote_tmp = f"/tmp/{local_csv.name}"
    remote_final = f"/var/lib/mysql-files/{local_csv.name}"

    # -----------------------------------------------------------------------
    # Copiar archivo al servidor
    # -----------------------------------------------------------------------

    subprocess.run(["scp", str(local_csv), f"{ssh_alias}:{remote_tmp}",], check=True)

    # -----------------------------------------------------------------------
    # Mover archivo a la carpeta permitida por MySQL
    # -----------------------------------------------------------------------

    cmd = (
        f"sudo mv '{remote_tmp}' '{remote_final}' && "
        f"sudo chown mysql:mysql '{remote_final}' && "
        f"sudo chmod 640 '{remote_final}'"
    )

    subprocess.run(["ssh", ssh_alias, cmd], check=True)

    print(f"Usando tabla {table} en base de datos {os.getenv('DB_NAME')}.")

    # -----------------------------------------------------------------------
    # Conectar a MySQL
    # -----------------------------------------------------------------------

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            sql = f"""
                LOAD DATA INFILE '{remote_final}'
                INTO TABLE {table}
                CHARACTER SET utf8mb4
                FIELDS TERMINATED BY ','
                ENCLOSED BY '"'
                LINES TERMINATED BY '\\n'
                IGNORE 1 LINES
                (
                    COD_PRT,
                    PPU,
                    COD_VEHICULO,
                    COD_COMBUSTIBLE,
                    COD_SERVICIO,
                    MARCA,
                    MODELO,
                    ANO_FABRICACION,
                    @NUM_MOTOR,
                    @NUM_CHASIS,
                    @VIN,
                    @KILOMETRAJE,
                    NUM_CERTIFICADO,
                    @FEC_REVISION,
                    @FEC_VENCIMIENTO,
                    HORA_INI,
                    HORA_FIN,
                    RESULTADO_CRT,
                    @FEC_VENCIMIENTO_GASES,
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
                SET
                    NUM_MOTOR = NULLIF(@NUM_MOTOR, ''),
                    NUM_CHASIS = NULLIF(@NUM_CHASIS, ''),
                    VIN = NULLIF(@VIN, ''),
                    KILOMETRAJE = NULLIF(@KILOMETRAJE, ''),
                    FEC_REVISION = NULLIF(@FEC_REVISION, ''),
                    FEC_VENCIMIENTO = NULLIF(@FEC_VENCIMIENTO, ''),
                    FEC_VENCIMIENTO_GASES =
                        NULLIF(@FEC_VENCIMIENTO_GASES, '');
            """

            cur.execute(sql)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

        # -------------------------------------------------------------------
        # Eliminar archivo temporal del servidor
        # -------------------------------------------------------------------
        
        subprocess.run(["ssh", ssh_alias, f"sudo rm -f '{remote_final}'"], check=True)

    return True


# ---------------------------------------------------------------------------
# Procesar archivos CSV
# ---------------------------------------------------------------------------

def upload(input_folder, move_folder, table, ssh_alias):
    """Procesar todos los CSV pendientes de carga."""

    input_folder = Path(input_folder)
    move_folder = Path(move_folder)
    move_folder.mkdir(parents=True, exist_ok=True)

    # Obtener archivos CSV y ordenarlos cronológicamente
    csv_files = sorted(
        [
            file
            for file in input_folder.iterdir()
            if file.is_file() and file.suffix.lower() == ".csv"
        ], key=lambda file: extract_year_month(file.name)
    )

    if not csv_files:
        print("[INFO] No hay archivos CSV para subir.")
        return

    print(f"Se encontraron {len(csv_files)} archivos para subir.\n")

    # Procesar cada archivo
    for file in csv_files:
        print(f"[UPLOAD] Subiendo: {file.name}...")
        try:
            import_csv_via_ssh_load_infile(file, table=table, ssh_alias=ssh_alias)
            shutil.move(str(file), str(move_folder / file.name))
            print(f"[OK] Subido y movido: {file.name}")

        except Exception as e:
            print(f"[ERROR] Subiendo {file.name}: {e}")

        print("-" * 80)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Carga archivos CSV de PRT en MySQL."
    )

    parser.add_argument(
        "--input-folder",
        type=Path,
        default=DEFAULT_INPUT_FOLDER,
        help="Carpeta con los CSV procesados.",
    )

    parser.add_argument(
        "--move-folder",
        type=Path,
        default=DEFAULT_MOVE_FOLDER,
        help="Carpeta donde se moverán los CSV cargados.",
    )

    parser.add_argument(
        "--table",
        default=os.getenv("TABLE_NAME_TMP"),
        help="Tabla MySQL de destino.",
    )

    parser.add_argument(
        "--ssh-alias",
        default=DEFAULT_SSH_ALIAS,
        help="Alias SSH del servidor.",
    )

    args = parser.parse_args()

    if not args.table:
        parser.error("No se especificó --table y TABLE_NAME_TMP no está definido en .env.")

    upload(
        input_folder=args.input_folder,
        move_folder=args.move_folder,
        table=args.table,
        ssh_alias=args.ssh_alias
    )

if __name__ == "__main__":
    main()

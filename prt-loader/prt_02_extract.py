# 02 - Extract
# Extraer .zip y moverlos a otra carpeta

import argparse
import os
import shutil
import zipfile


DEFAULT_ZIP_FOLDER = "D:/ferna/Downloads/DL - Calistoweb/PRT"
DEFAULT_EXTRACT_FOLDER = "D:/ferna/Downloads/DL - Calistoweb/PRT/extracted"
DEFAULT_MOVE_FOLDER = "D:/ferna/Downloads/DL - Calistoweb/PRT/zip"


def extract(zip_file, zip_folder, extract_folder):
    """
    Extrae un archivo ZIP en la carpeta indicada.
    """

    zip_path = os.path.join(zip_folder, zip_file)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)
        print(f"[OK] Extraído: {zip_file}")
    except zipfile.BadZipFile:
        print(f"[ERROR] Archivo ZIP inválido: {zip_file}")
    except Exception as e:
        print(f"[ERROR] Problema extrayendo {zip_file}: {e}")


def delete(zip_file, zip_folder):
    """
    Elimina un archivo ZIP.
    """

    zip_path = os.path.join(zip_folder, zip_file)

    try:
        os.remove(zip_path)
        print(f"[OK] Eliminado: {zip_file}")
    except Exception as e:
        print(f"[ERROR] Problema eliminando {zip_file}: {e}")


def move(zip_file, zip_folder, move_folder):
    """
    Mueve un archivo ZIP a la carpeta indicada.
    """

    zip_path = os.path.join(zip_folder, zip_file)
    move_path = os.path.join(move_folder, zip_file)

    try:
        shutil.move(zip_path, move_path)
        print(f"[OK] Movido: {zip_file}")
    except Exception as e:
        print(f"[ERROR] Problema moviendo {zip_file}: {e}")


def main(zip_folder, extract_folder, move_folder):
    # Crear carpetas si no existen
    os.makedirs(extract_folder, exist_ok=True)
    os.makedirs(move_folder, exist_ok=True)

    # Obtener lista de archivos .zip
    zip_files = [
        f for f in os.listdir(zip_folder)
        if f.lower().endswith(".zip")
    ]

    if not zip_files:
        print("[INFO] No se encontraron archivos ZIP.")
        return

    print(f"Se encontraron {len(zip_files)} archivos ZIP.\n")

    # Extraer los archivos ZIP
    for zip_file in zip_files:
        extract(zip_file, zip_folder, extract_folder)

    print(80 * "-")
    print("Extracción terminada.")

    # Mover los archivos ZIP
    for zip_file in zip_files:
        move(zip_file, zip_folder, move_folder)

    print(80 * "-")
    print(f"Archivos ZIP movidos a {move_folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrae archivos ZIP y luego los mueve a otra carpeta."
    )

    parser.add_argument(
        "--zip-folder",
        default=DEFAULT_ZIP_FOLDER,
        help="Carpeta donde se encuentran los archivos ZIP."
    )

    parser.add_argument(
        "--extract-folder",
        default=DEFAULT_EXTRACT_FOLDER,
        help="Carpeta donde se extraerán los archivos."
    )

    parser.add_argument(
        "--move-folder",
        default=DEFAULT_MOVE_FOLDER,
        help="Carpeta donde se moverán los ZIP después de extraerlos."
    )

    args = parser.parse_args()

    main(args.zip_folder, args.extract_folder, args.move_folder)

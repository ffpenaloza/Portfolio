# 03 - Process
# Eliminar columnas innecesarias, normalizar datos y convertir a CSV

import argparse
import shutil
from pathlib import Path

import pandas as pd

DEFAULT_INPUT_FOLDER = Path("D:/ferna/Downloads/DL - Calistoweb/PRT/extracted")
DEFAULT_OUTPUT_FOLDER = Path("D:/ferna/Downloads/DL - Calistoweb/PRT/extracted_cleaned")
DEFAULT_MOVE_FOLDER = Path("D:/ferna/Downloads/DL - Calistoweb/PRT/extracted/processed")

COLUMNS_TO_KEEP = [
    "COD_PRT",
    "PPU",
    "COD_VEHICULO",
    "COD_COMBUSTIBLE",
    "COD_SERVICIO",
    "MARCA",
    "MODELO",
    "ANO_FABRICACION",
    "NUM_MOTOR",
    "NUM_CHASIS",
    "VIN",
    "KILOMETRAJE",
    "NUM_CERTIFICADO",
    "FEC_REVISION",
    "FEC_VENCIMIENTO",
    "HORA_INI",
    "HORA_FIN",
    "RESULTADO_CRT",
    "FEC_VENCIMIENTO_GASES",
    "RESULTADO_CRT_GASES",
    "IDENTIFICACION",
    "VISUAL",
    "LUCES",
    "ALINEACION",
    "FRENOS",
    "HOLGURAS",
    "SUSPENSION",
    "GASES",
    "OPACIDAD",
]

DATE_COLUMNS = ["FEC_REVISION", "FEC_VENCIMIENTO", "FEC_VENCIMIENTO_GASES"]

def process_file(file, input_folder, output_folder, move_folder):
    """
    Procesa un archivo Excel:

    1. Lee las columnas seleccionadas.
    2. Limita la longitud de algunos campos.
    3. Normaliza las fechas.
    4. Guarda el resultado como CSV.
    5. Mueve el Excel original a la carpeta de procesados.
    """

    file_path = input_folder / file
    output_file = Path(file).with_suffix(".csv")
    output_path = output_folder / output_file
    processed_path = move_folder / file

    try:
        # Leer archivo Excel
        df = pd.read_excel(file_path, engine="openpyxl", usecols=COLUMNS_TO_KEEP)

        # Limitar longitud de campos
        for column in ["NUM_MOTOR", "NUM_CHASIS", "VIN"]:
            if column in df.columns:
                df[column] = df[column].astype("string").str[:50]

        # Normalizar fechas
        for column in DATE_COLUMNS:
            if column not in df.columns:
                continue

            s = df[column]
            # Si la columna ya es datetime
            if pd.api.types.is_datetime64_any_dtype(s):
                df[column] = s.dt.strftime("%Y-%m-%d")

            # Si toda la columna está vacía
            elif s.isna().all():
                df[column] = pd.NA
            else:
                # Convertir temporalmente a texto
                s_str = s.fillna("").astype(str)
                # Detectar fechas que ya están en YYYY-MM-DD
                mask_valid = s_str.str.match(r"^\d{4}-\d{2}-\d{2}$")

                # Valores que necesitan ser convertidos
                to_parse_idx = (~mask_valid) & (s_str != "")
                # Intentar convertir
                parsed = pd.to_datetime(s[to_parse_idx], errors="coerce", dayfirst=False)
                parsed_str = parsed.dt.strftime("%Y-%m-%d")

                # Construir nueva columna
                new_col = s.astype(object)
                new_col.loc[mask_valid] = (s_str.loc[mask_valid])
                new_col.loc[to_parse_idx] = parsed_str

                # Vacíos → NA
                new_col = new_col.where(new_col != "", pd.NA)
                df[column] = new_col

        # Guardar CSV
        df.to_csv(output_path, index=False)

        # Mover Excel original
        shutil.move(file_path, processed_path)
        return f"[OK] Procesado: {file}"

    except Exception as e:
        return f"[ERROR] Procesando {file}: {e}"


def process(input_folder, output_folder, move_folder):
    """
    Procesa todos los archivos Excel que aún no tengan
    un CSV correspondiente.
    """

    # Crear carpetas
    output_folder.mkdir(parents=True, exist_ok=True)
    move_folder.mkdir(parents=True, exist_ok=True)

    # Obtener Excel
    excel_files = [
        file
        for file in input_folder.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".xlsx"
    ]

    # Obtener CSV existentes
    csv_files = [
        file
        for file in output_folder.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".csv"
    ]

    csv_basenames = {file.stem for file in csv_files}

    # Filtrar los que aún no han sido procesados
    excel_files_to_process = [
        file
        for file in excel_files
        if file.stem not in csv_basenames
    ]

    if not excel_files_to_process:
        print("[INFO] No hay archivos nuevos para procesar.")
        return

    print(
        f"Se encontraron "
        f"{len(excel_files_to_process)} archivos "
        f"para procesar.\n"
    )

    # Procesar secuencialmente
    for file in excel_files_to_process:
        result = process_file(file.name, input_folder, output_folder, move_folder)
        print(result)

    print("\nProcesamiento terminado.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Procesa archivos Excel de PRT, "
            "los convierte a CSV y mueve los originales."
        )
    )

    parser.add_argument(
        "--input-folder",
        type=Path,
        default=DEFAULT_INPUT_FOLDER,
        help="Carpeta con los archivos Excel.",
    )

    parser.add_argument(
        "--output-folder",
        type=Path,
        default=DEFAULT_OUTPUT_FOLDER,
        help="Carpeta donde se guardarán los CSV.",
    )

    parser.add_argument(
        "--move-folder",
        type=Path,
        default=DEFAULT_MOVE_FOLDER,
        help="Carpeta donde se moverán los Excel procesados.",
    )

    args = parser.parse_args()

    process(args.input_folder, args.output_folder, args.move_folder)

if __name__ == "__main__":
    main()

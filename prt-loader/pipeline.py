# pipeline.py
# Orquestador del pipeline de datos PRT

import argparse
import subprocess
import sys

SCRIPTS = [
    "prt_01_download.py",
    "prt_02_extract.py",
    "prt_03_process.py",
    "prt_04_upload_tmp.py",
    "prt_05_insert_production.py",
]

def run_script(script, args=None):
    """
    Ejecuta un script del pipeline y detiene el proceso
    si el script termina con error.
    """

    command = [sys.executable, script]

    if args:
        command.extend(args)

    print("=" * 80)
    print(f"[START] {script}")
    print("=" * 80)

    subprocess.run(command, check=True)

    print(f"[OK] {script} terminado.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Ejecuta el pipeline completo de datos PRT."
    )

    parser.add_argument(
        "--periods",
        nargs="+",
        required=True,
        help="Períodos a descargar en formato YYYY-MM. Ejemplo: 2026-07 2026-08"
    )

    args = parser.parse_args()
    
    # 1. Download
    run_script("prt_01_download.py", ["--periods", *args.periods])

    # 2. Extract
    run_script("prt_02_extract.py")

    # 3. Process
    run_script("prt_03_process.py")

    # 4. Upload to staging
    run_script("prt_04_upload_tmp.py")

    # 5. Insert into production
    run_script("prt_05_insert_production.py")

    # Finished
    print("=" * 80)
    print("[OK] Pipeline PRT terminado correctamente.")
    print("=" * 80)

if __name__ == "__main__":
    main()

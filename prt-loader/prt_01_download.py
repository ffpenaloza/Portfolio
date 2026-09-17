# 01 - Download
# Descarga archivos de la página de PRT
# https://www.prt.cl/Descargas/docs/

import argparse
import os
import requests

BASE_URL = "https://www.prt.cl/Descargas/docs/"
DOWNLOAD_FOLDER = "D:/ferna/Downloads/DL - Calistoweb/PRT"

MONTH_NAMES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

def download(periods):
    """
    Descarga los archivos PRT correspondientes a los períodos indicados.

    periods:
        Lista de períodos en formato YYYY-MM.
        Ejemplo: ["2026-07", "2026-08"]
    """

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    for period in periods:
        try:
            year, month_number = period.split("-")
            year = int(year)
            month_number = int(month_number)

            if not 1 <= month_number <= 12:
                raise ValueError("Mes fuera de rango.")

        except ValueError:
            print(f"[ERROR] Período inválido: {period}. Use YYYY-MM.")
            continue

        month = MONTH_NAMES[month_number - 1]
        month_short = month[:3].lower()

        url = (
            f"{BASE_URL}{year}/{month_number}.{month}/"
            f"SGPRT_RB_{month_short}-{year}.zip"
        )

        filename = f"SGPRT_RB_{month_short}-{year}.zip"
        local = os.path.join(DOWNLOAD_FOLDER, filename)

        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(local, "wb") as file:
                    file.write(response.content)
                print(f"[OK] Descargado: {month}, {year}.")
            else:
                print(
                    f"[ERROR] No encontrado {url}: "
                    f"{month}, {year} "
                    f"(HTTP {response.status_code})."
                )

        except requests.RequestException as e:
            print(
                f"[ERROR] Error al descargar {url}: "
                f"{month}, {year} -> {e}."
            )
        print(80 * "-")

    print("Terminado.")


def main():
    parser = argparse.ArgumentParser(
        description="Descarga archivos de datos de PRT."
    )

    parser.add_argument(
        "--periods",
        nargs="+",
        required=True,
        help="Períodos a descargar en formato YYYY-MM. Ejemplo: 2026-07 2026-08"
    )
    
    args = parser.parse_args()
    download(args.periods)

if __name__ == "__main__":
    main()

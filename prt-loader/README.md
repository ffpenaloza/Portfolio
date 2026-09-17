# PRT Data Pipeline

Pipeline de datos para la recopilación, procesamiento y carga de información histórica de **Plantas de Revisión Técnica (PRT) de Chile**.

El proyecto automatiza el procesamiento de los archivos publicados por PRT y los transforma en datos estructurados que posteriormente son almacenados en una base de datos MySQL.

Los datos procesados alimentan un servicio web de **CalistoWeb**, donde pueden ser consultados directamente por usuarios.

**Consulta los datos:** [https://auto.calistoweb.cl](https://auto.calistoweb.cl?utm_source=github)

---

## Descripción

El pipeline implementa un proceso ETL compuesto por cinco etapas para la obtención, procesamiento y carga en una base de datos MySQL:

```text
Datos PRT
   │
   ▼
01 Download
   │
   ▼
02 Extract
   │
   ▼
03 Process
   │
   ▼
04 Upload
   │
   ▼
05 Insert Production
   │
   ▼
MySQL
   │
   ▼
CalistoWeb - Historial PRT
```

Cada etapa tiene una responsabilidad específica y puede ejecutarse de manera independiente. El archivo `pipeline.py` permite ejecutar el proceso completo de forma secuencial.

---

## Etapas del pipeline

### 01 — Download

Descarga desde el sitio de PRT los archivos correspondientes a los períodos solicitados.

Los períodos se especifican utilizando el formato:

```text
YYYY-MM
```

Por ejemplo:

```bash
python prt_01_download.py --periods 2026-07 2026-08
```

---

### 02 — Extract

Extrae los archivos `.zip` descargados y organiza los archivos resultantes en las carpetas correspondientes.

Los archivos ZIP procesados se conservan en una carpeta separada.

```bash
python prt_02_extract.py
```

---

### 03 — Process

Procesa los archivos Excel obtenidos durante la extracción.

Esta etapa:

* selecciona las columnas relevantes;
* normaliza determinados campos;
* limita la longitud de identificadores;
* normaliza las fechas;
* convierte los archivos Excel a CSV;
* mueve los archivos originales una vez procesados.

```bash
python prt_03_process.py
```

---

### 04 — Upload

Carga los archivos CSV procesados a una tabla temporal de MySQL.

La transferencia utiliza:

* SSH;
* SCP;
* `LOAD DATA INFILE`.

Este mecanismo permite realizar una carga masiva de los datos en lugar de insertar los registros individualmente.

```bash
python prt_04_upload_tmp.py
```

---

### 05 — Insert Production

Traspasa los datos desde la tabla temporal hacia la tabla de producción.

```text
prt_b_part_TMP
       │
       │ INSERT ... SELECT
       ▼
prt_b_part
```

Una vez completado correctamente el traspaso, la tabla temporal es limpiada.

```bash
python prt_05_insert_production.py
```

---

## Orquestación

Las cinco etapas pueden ejecutarse individualmente, pero también existe un orquestador que ejecuta todo el pipeline en el orden correspondiente.

Por ejemplo:

```bash
python pipeline.py --periods 2026-07 2026-08
```

El flujo será:

```text
[1] Download
       ↓
[2] Extract
       ↓
[3] Process
       ↓
[4] Upload
       ↓
[5] Insert Production
```

Si una etapa termina con error, el pipeline se detiene y las etapas posteriores no se ejecutan.

---

## Estructura del proyecto

```text
.
├── pipeline.py
├── prt_01_download.py
├── prt_02_extract.py
├── prt_03_process.py
├── prt_04_upload_tmp.py
├── prt_05_insert_production.py
│
├── MySQL/
│   ├── crear_tabla_plantas_revision.sql
│   └── crear_tablas_revision.sql
│
├── .env
└── .gitignore
```

---

## Flujo de archivos

Durante el proceso, los archivos pasan por diferentes estados:

```text
PRT/
│
├── *.zip
│
├── zip/
│   └── *.zip
│
├── extracted/
│   ├── *.xlsx
│   └── processed/
│       └── *.xlsx
│
└── extracted_cleaned/
    ├── *.csv
    └── uploaded/
        └── *.csv
```

Esta separación permite identificar en qué etapa se encuentra cada archivo y conservar los archivos procesados cuando sea necesario.

---

## Base de datos

El pipeline utiliza una tabla temporal y una tabla de producción.

```text
PRT files
    │
    ▼
prt_b_part_TMP
    │
    │ INSERT ... SELECT
    ▼
prt_b_part
```

La tabla temporal permite separar la carga masiva de los datos del proceso de incorporación a la tabla de producción.

Esto también permite que los datos permanezcan en staging si ocurre un error durante la carga hacia producción.

---

## Configuración

El proyecto utiliza **python-dotenv** para cargar variables de configuración desde un archivo `.env`.

El archivo `.env` debe ubicarse en la raíz del proyecto y contiene las credenciales y parámetros necesarios para conectarse a la base de datos y al servidor SSH.

Ejemplo:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=usuario
DB_PASSWORD=contraseña
DB_NAME=base_de_datos

TABLE_NAME_TMP=prt_b_part_TMP
TABLE_NAME=prt_b_part

SSH_ALIAS=alias
```

Las variables se cargan mediante `python-dotenv` y se acceden desde Python a través de las variables de entorno.

---

## Requisitos

* Python 3
* MySQL
* Acceso SSH al servidor de base de datos
* `ssh`
* `scp`

Dependencias Python:

```bash
pip install requests pandas openpyxl pymysql python-dotenv
```

o

```bash
conda install requests pandas openpyxl pymysql python-dotenv
```

---

## Seguridad

Este repositorio no contiene credenciales, contraseñas ni archivos `.env`.

Antes de ejecutar el pipeline, crea un archivo `.env` con tus propios parámetros de conexión.

El archivo `.env` debe mantenerse fuera del control de versiones y no debe compartirse públicamente.

---

## Consulta de los datos

El resultado final del pipeline se utiliza en **CalistoWeb**.

Los usuarios pueden consultar la información procesada directamente desde:

[https://auto.calistoweb.cl](https://auto.calistoweb.cl?utm_source=github)

El pipeline y la aplicación de consulta son componentes independientes:

```text
              PRT
               │
               ▼
        Data Pipeline
               │
               ▼
             MySQL
               │
               ▼
       Auto CalistoWeb
               │
               ▼
             Usuario
```

---

## Tecnologías

* **Python**
* **Pandas**
* **OpenPyXL**
* **Requests**
* **PyMySQL**
* **python-dotenv**
* **MySQL**
* **SSH / SCP**

El proyecto utiliza `pathlib.Path` para el manejo de rutas en las etapas que requieren operaciones con archivos.

---

## Propósito del proyecto

Este proyecto automatiza un proceso real de recopilación y transformación de datos públicos de PRT y constituye la infraestructura de datos utilizada para proporcionar información histórica de revisiones técnicas a través del servicio web de CalistoWeb.

La arquitectura modular permite ejecutar, mantener y evolucionar cada etapa de manera independiente, además de facilitar futuras mejoras en automatización, almacenamiento y procesamiento de datos.

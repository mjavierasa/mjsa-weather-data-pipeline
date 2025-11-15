"""
Script principal : Weather Data Pipeline.

Coordina la ejecución completa del flujo ETL:
1. Extracción de datos meteorológicos desde la API pública del NWS (weather.gov).
2. Transformación y almacenamiento en una base SQLite local.
3. Validaciones y análisis sobre los datos persistidos.

Supuestos:
- El entorno virtual (venv) está activado.
- 'config.py' contiene los parámetros y estaciones correctas.
- Las dependencias están instaladas desde 'requirements.txt'.
"""

from pipeline import run_pipeline
from utils import run_basic_validations
from queries import run_analytics


def main():

    print("===========================================")
    print("   INICIO DEL PROCESO - WEATHER PIPELINE   ")
    print("===========================================\n")

    # 1. ETL - Extracción, transformación y carga
    print("--- Ejecución del pipeline ETL ---")
    run_pipeline()

    # 2. Validaciones de consistencia
    print("\n--- Validaciones básicas ---")
    run_basic_validations()

    # 3. Consultas analíticas finales
    print("\n--- Consultas analíticas ---")
    run_analytics()

    print("===========================================\n")
    print("\n --- Proceso completado exitosamente.")
    print("===========================================\n")


if __name__ == "__main__":
    main()

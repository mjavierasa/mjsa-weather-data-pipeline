"""
Módulo principal del pipeline ETL para obtención de datos meteorológicos.

Flujo:
1. Extrae observaciones desde la API pública del National Weather Service (weather.gov)
2. Transforma las respuestas en un DataFrame estandarizado
3. Carga los registros en una base SQLite con control de duplicados (idempotencia)

Supuestos:
- Los códigos de estación definidos en config.STATIONS existen en el endpoint del NWS
- La API devuelve observaciones en formato GeoJSON válido
- Los datos se procesan en UTC y se almacenan en formato ISO 8601
"""

from datetime import datetime, timedelta, timezone
import requests
import pandas as pd
from sqlalchemy import text
from database import get_engine, create_table
from config import BASE_URL, STATIONS, USER_AGENT, API_TIMEOUT, DB_PATH


def fetch_station_data(station_id):
    """
    Obtiene los últimos 21 días de observaciones de una estación del NWS
    y devuelve una lista de registros normalizados para carga en base de datos.
    """
    # Calcular fecha de inicio (últimos 21 días en formato ISO 8601 UTC)
    start_date = (datetime.now(timezone.utc) - timedelta(days=21)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Construir endpoint y cabeceras de solicitud
    url = f"{BASE_URL}/stations/{station_id}/observations?start={start_date}"
    headers = {"User-Agent": USER_AGENT}

    try:
        # Llamada a la API pública del NWS
        response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Validar estructura básica de respuesta
        if "features" not in data:
            print(f"Respuesta inesperada para {station_id}: formato inválido.")
            return []

        records = []
        for obs in data["features"]:
            props = obs.get("properties", {})
            geometry = obs.get("geometry", {}).get("coordinates", [None, None])
            timestamp = props.get("timestamp")

            if not timestamp:
                continue  # Saltar observaciones sin hora válida

            records.append({
                "ID_estacion": station_id,
                "Nombre_estacion": props.get("station", station_id),
                "zona_horaria": props.get("timestamp"),
                "latitud": geometry[1],
                "longitud": geometry[0],
                "hora_observacion": timestamp,
                "temperatura": round(props.get("temperature", {}).get("value") or 0, 2),
                "velocidad_viento": round(props.get("windSpeed", {}).get("value") or 0, 2),
                "humedad": round(props.get("relativeHumidity", {}).get("value") or 0, 2),
                "unique_key": f"{station_id}_{timestamp}"
            })

        return records

    except requests.exceptions.RequestException as e:
        print(f"Error en estación {station_id}: {e}")
        return []
    except Exception as e:
        print(f"Error procesando datos de {station_id}: {e}")
        return []


def run_pipeline():
    """Orquesta el flujo ETL completo y ejecuta el análisis posterior."""
    print("Inicio del pipeline de datos meteorológicos.\n")

    all_data = []
    for station in STATIONS:
        print(f"Obteniendo datos de estación {station} ...")
        station_data = fetch_station_data(station)
        if station_data:
            all_data.extend(station_data)

    if not all_data:
        print("No se obtuvieron datos válidos de las estaciones.")
        return

    df = pd.DataFrame(all_data)
    print(f"{len(df)} registros obtenidos correctamente.\n")

    engine = get_engine(DB_PATH)
    create_table(engine, "weather_data", df)

    insert_sql = text("""
        INSERT OR IGNORE INTO weather_data 
        (ID_estacion, Nombre_estacion, zona_horaria, latitud, longitud, 
         hora_observacion, temperatura, velocidad_viento, humedad, unique_key)
        VALUES (:ID_estacion, :Nombre_estacion, :zona_horaria, :latitud, :longitud, 
                :hora_observacion, :temperatura, :velocidad_viento, :humedad, :unique_key)
    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, df.to_dict(orient="records"))

    print(f"Datos almacenados exitosamente en {DB_PATH}.\n")

    # Ejecutar análisis posterior
    from queries import run_analytics
    run_analytics()

    # Resumen final por estación
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    print("Resumen de observaciones por estación:\n")
    for row in conn.execute("SELECT ID_estacion, COUNT(*) FROM weather_data GROUP BY ID_estacion;"):
        print(f"{row[0]}: {row[1]} registros")
    conn.close()

    print("\nPipeline completado correctamente.\n")


if __name__ == "__main__":
    run_pipeline()

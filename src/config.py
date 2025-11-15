"""
Archivo de configuración: Proyecto Weather Data Pipeline.

Define las variables globales del pipeline, incluyendo:
- Rutas de la base de datos.
- Parámetros de la API pública del National Weather Service (weather.gov).
- Identificadores de las cinco estaciones seleccionadas para análisis.
- Parámetros de conexión y control de ejecución.

Supuestos:
1. Se utiliza la API pública documentada en: https://www.weather.gov/documentation/services-web-api
2. Las estaciones incluidas en 'selected_stations.csv' fueron previamente seleccionadas 
   desde 'stations_sample.csv' mediante un muestreo aleatorio reproducible.
3. El sistema se ejecuta en horario UTC y utiliza formato ISO 8601 para consistencia temporal.

"""

import pandas as pd
import os

# Ruta de la base de datos local SQLite
DB_PATH = "weather_data.db"

# API pública del National Weather Service (NWS)
BASE_URL = "https://api.weather.gov"

# Identificador API pública del NWS 
USER_AGENT = "WeatherDataCollector/1.0 (m.javiera.sepulveda@gmail.com)"

# Lectura de estaciones seleccionadas previamente (5 elegidas por muestreo reproducible)
if os.path.exists("selected_stations.csv"):
    df_stations = pd.read_csv("selected_stations.csv")
    STATIONS = df_stations["ID_estacion"].tolist()
else:
    STATIONS = []
    print("Advertencia: no se encontró 'selected_stations.csv'. El pipeline se ejecutará sin estaciones definidas.")

# Parámetros adicionales del pipeline
API_TIMEOUT = 60              # Tiempo máximo de espera para solicitudes HTTP (segundos)
FETCH_INTERVAL = 3600         # Intervalo de actualización (segundos) — reservado para automatizaciones
LOG_FILE = "weather_data.log" # Archivo de registro (pendiente de integración con módulo logging)
MAX_RETRIES = 3               # Número máximo de reintentos por estación
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # Formato ISO 8601

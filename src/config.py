"""
Configuración global del proyecto Weather Data Pipeline.

Define:
- Ruta de la base de datos local.
- Parámetros de la API pública del National Weather Service (weather.gov)
- Estaciones seleccionadas para el análisis
- Parámetros de control de ejecución (tiempos, reintentos, formato de fechas)

Supuestos:
1. Se utiliza la API pública documentada en:
   https://www.weather.gov/documentation/services-web-api
2. 'selected_stations.csv' contiene las estaciones seleccionadas mediante
   un muestreo aleatorio reproducible a partir de 'stations_sample.csv'
3. El sistema opera en horario UTC y utiliza formato ISO 8601 para consistencia temporal
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
API_TIMEOUT = 60                     # Tiempo máximo de espera para solicitudes HTTP (segundos)
FETCH_INTERVAL = 3600                # Intervalo de actualización (segundos) — reservado para automatizaciones
LOG_FILE = "weather_data.log"        # Archivo de registro (pendiente de integración con módulo logging)
MAX_RETRIES = 3                      # Número máximo de reintentos por estación
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"  # Formato ISO 8601

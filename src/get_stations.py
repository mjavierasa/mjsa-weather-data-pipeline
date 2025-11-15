"""
Script GS: Obtención y exploración de estaciones meteorológicas disponibles 
en la API pública del National Weather Service (weather.gov).

Uso principal:
Permite listar y validar los códigos de estación (`stationIdentifier`) 
que pueden utilizarse en el pipeline ETL antes de definirlos en `config.py`

Genera un archivo CSV con las estaciones obtenidas, incluyendo:
- ID de estación
- Nombre
- Coordenadas (latitud / longitud)
- Zona horaria
- Elevación (en metros)

"""

import requests
import pandas as pd

# Endpoint público del NWS
URL = "https://api.weather.gov/stations"

# Cabecera de identificación de cliente
HEADERS = {"User-Agent": "WeatherDataPipeline/1.0 (m.javiera.sepulveda@gmail.com)"}


def get_stations(limit=50, output_path="stations_sample.csv"):

    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "features" not in data:
            print("Respuesta inesperada del endpoint de estaciones.")
            return pd.DataFrame()

        stations = []
        for f in data["features"][:limit]:
            props = f.get("properties", {})
            stations.append({
                "ID_estacion": props.get("stationIdentifier"),
                "Nombre_estacion": props.get("name"),
                "latitud": props.get("latitude"),
                "longitud": props.get("longitude"),
                "zona_horaria": props.get("timeZone"),
                "elevacion_metros": props.get("elevation", {}).get("value")
            })

        df = pd.DataFrame(stations)
        df.to_csv(output_path, index=False)
        print(f"{len(df)} estaciones guardadas correctamente en '{output_path}'.")
        return df

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error procesando datos de estaciones: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    get_stations(limit=100)
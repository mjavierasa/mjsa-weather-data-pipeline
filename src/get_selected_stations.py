"""
Script GSS: Selección de estaciones meteorológicas específicas 
desde el archivo `stations_sample.csv` previamente descargado.

Uso principal:
Generar un subconjunto reproducible de 5 estaciones para utilizar 
en el pipeline ETL del proyecto.

Detalles:
- La selección se realiza de forma aleatoria pero controlada 
  mediante una semilla fija (`random_state=42`).
- Las estaciones seleccionadas se guardan en el archivo 
  `selected_stations.csv`, que será leído por `config.py`.

Supuestos:
- El archivo `stations_sample.csv` ya fue generado mediante `get_stations.py`.
- Las columnas contienen los campos esperados: 
  ID_estacion, Nombre_estacion, latitud, longitud, zona_horaria, elevacion_metros.

"""

import pandas as pd

# Leer el CSV original con todas las estaciones
df_stations = pd.read_csv("stations_sample.csv")

# Seleccionar 5 estaciones aleatorias reproducibles
selected = df_stations.sample(5, random_state=42)

print("=== Estaciones seleccionadas (semilla 42) ===\n")
print(selected[["ID_estacion", "Nombre_estacion", "latitud", "longitud", "zona_horaria", "elevacion_metros"]])

# Guardar las estaciones elegidas en un nuevo CSV
selected.to_csv("selected_stations.csv", index=False)
print("\n---Archivo 'selected_stations.csv' creado correctamente.")

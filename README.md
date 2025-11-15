# Weather Data Pipeline  
Prueba Técnica — LATAM Airlines  
**Fecha:** 14 de noviembre de 2025  

---

# Descripción general

El objetivo fue diseñar un pipeline de datos que ingiera, procese y analice información meteorológica proveniente de la API pública del **National Weather Service (weather.gov)**, aplicando principios de ingeniería de datos, control de idempotencia y consultas analíticas SQL.

---
## Objetivo
Diseñar un pipeline capaz de:
- Obtener datos meteorológicos desde la API  
- Almacenarlos correctamente  
- Analizarlos mediante consultas SQL
---
## Conjunto de datos
- Estaciones: `/stations`  
- Observaciones: `/stations/{station_id}/observations`
---

## Especificaciones
- Primera ejecución → **21 días**  
- Reejecuciones → solo registros nuevos  
- Requisito obligatorio → **idempotencia**

---

# Arquitectura del proyecto

```bash
weather_pipeline/
│
├── src/
│   ├── config.py            # Parámetros globales y estaciones seleccionadas
│   ├── database.py          # Conexión y creación dinámica de tablas SQLite
│   ├── pipeline.py          # Lógica principal ETL
│   ├── queries.py           # Consultas analíticas SQL sobre los datos cargados
│   ├── utils.py             # Validaciones automáticas del proceso
│   ├── get_stations.py      # Exploración y filtrado de estaciones desde la API
│   └── main.py              # Orquestador general del pipeline
│
├── selected_stations.csv    # Estaciones seleccionadas para ingesta
├── stations_sample.csv      # Muestra original obtenida desde la API pública
├── requirements.txt         # Dependencias del proyecto
├── .gitignore               # Exclusiones
└── README.md                # Documentación del proyecto
```

---

# Diagrama del sistema

```text
                 +----------------------+
                 |  National Weather     |
                 |     Service API       |
                 |     (weather.gov)     |
                 +----------+-------------+
                            |
                            |   GeoJSON (21 días)
                            v
    +-----------------+   Extract   +-------------------+
    | get_stations.py | ----------> | pipeline.py       |
    +-----------------+             | (Extracción)       |
                                    +---------+----------+
                                              |
                                              v
                               +---------------------------+
                               | Transform                |
                               | pandas.DataFrame         |
                               | - Normalización          |
                               | - Estandarización        |
                               | - unique_key             |
                               +-------------+-------------+
                                             |
                                             v
                               +---------------------------+
                               | Load                     |
                               | SQLAlchemy + SQLite      |
                               | - Tablas dinámicas       |
                               | - INSERT OR IGNORE       |
                               +-------------+-------------+
                                             |
                                             v
                      +-----------------------------------------+
                      | Base de datos: weather_data.db          |
                      +-----------------------------------------+
                                             |
                                             v
  +-------------------------+       +-----------------------------+
  | utils.py (validaciones) |       | queries.py (analíticas)    |
  +-------------------------+       +-----------------------------+
  | - frescura de datos     |       | - Query 1: temp. semanal    |
  | - conteo registros      |       | - Query 2: viento           |
  | - fecha última obs      |       | - Query 3: humedad          |
  +-------------------------+       | - Query 4: variación diaria |
                                    +-----------------------------+
```


---
---

## Flujo ETL

1. **Extracción (Extract):**  
   Obtención de los últimos 21 días de observaciones desde  
   `/stations/{station_id}/observations`.  
   - API base: `https://api.weather.gov`  
   - Formato: GeoJSON  
   - Cabecera: `User-Agent` personalizada  
   - Manejo de respuestas vacías o incompletas  

2. **Transformación (Transform):**  
   - Normalización en `pandas.DataFrame`  
   - Campos estandarizados:  
     `ID_estacion`, `Nombre_estacion`, `zona_horaria`, `latitud`, `longitud`,  
     `hora_observacion`, `temperatura`, `velocidad_viento`, `humedad`  
   - **Idempotencia:** clave única `unique_key = {ID_estacion}_{timestamp}`  

3. **Carga (Load):**  
   - Motor de base de datos: **SQLite**  
   - ORM: **SQLAlchemy**  
   - Inserción idempotente mediante `INSERT OR IGNORE`  

---

## Consultas analíticas

Implementadas en `queries.py` usando SQL nativo:

| Query | Descripción |
|-------|--------------|
| 1 | Temperatura media observada de la última semana (lunes a domingo) |
| 2 | Máximo cambio de velocidad del viento (últimos 7 días) |
| 3 | Mínima y máxima humedad por día |
| 4 | Variación diaria promedio de temperatura y humedad respecto al día anterior |

> *Nota:* Queries realizadas en base a los requerimientos del caso técnico.


---

## Validaciones automáticas

Antes de ejecutar las consultas analíticas, el módulo `utils.py` realiza verificaciones:

| Validación | Propósito |
|-------------|------------|
| Temperatura promedio (últimos 7 días) | Comprobar coherencia térmica |
| Conteo total de registros | Validar carga y completitud |
| Última fecha de observación registrada | Confirmar frescura de datos |

Estas verificaciones garantizan la **consistencia temporal** y la **calidad del dataset**.

---

## Supuestos del desarrollo

1. La API pública del **National Weather Service** responde en formato **GeoJSON**, conforme a su documentación oficial:  
   https://www.weather.gov/documentation/services-web-api
2. Todas las marcas de tiempo se almacenan en formato **ISO 8601 (UTC)**.  
3. El pipeline es **idempotente**: múltiples ejecuciones no generan duplicados.  
4. Se utiliza **SQLite** por su portabilidad; en entornos productivos puede reemplazarse por **PostgreSQL** o **MySQL**.  
5. Se implementa **SQLAlchemy** como **ORM**, permitiendo conectar Python con la base sin escribir SQL manual.  
6. Las respuestas vacías o erróneas no detienen la ejecución.  
7. Desarrollado y probado en **Python 3.9+ (macOS, LibreSSL 2.8.3)**.  
   Durante la ejecución puede aparecer la siguiente advertencia del entorno SSL:

   `urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'.`

   Esta advertencia no detiene ni afecta la ejecución del pipeline en este contexto de prueba,  
   pero en un entorno productivo se recomienda usar una versión de Python compilada con **OpenSSL ≥ 1.1.1**.



---

## Estaciones seleccionadas

Archivo: `selected_stations.csv`

| ID_estacion | Nombre_estacion          | Zona horaria         | Elevación (m) |
|--------------|--------------------------|----------------------|----------------|
| 001AS        | Poloa_Wx                 | Pacific/Pago_Pago    | 142.95 |
| 001SE        | SCE Glen Way             | America/Los_Angeles  | 409.04 |
| 003PG        | Loma Chiquita West       | America/Los_Angeles  | 794.91 |
| 004HC        | 3010 SH 288 at MacGregor | America/Chicago      | 13.10 |
| 006MD        | College Park 2 N         | America/New_York     | 28.95 |

> *Nota:* Al realizar la selección aleatoria y reproducible resultaron cuatro estaciones con datos disponibles y una sin observaciones recientes, lo que simula un escenario real.

---

## Ejecución local

~~~bash
# 1. Clonar el repositorio
git clone https://github.com/mjavierasa/weather-data-pipeline.git
cd weather-data-pipeline

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate   # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el pipeline completo
python3 src/main.py
~~~

---

# Dependencias principales

| Paquete | Uso |
|---------|-----|
| requests | Consumo de API |
| pandas | Transformación de datos |
| SQLAlchemy | ORM |
| pytz / dateutil | Manejo de fechas |

---

# Reproducibilidad y calidad

- `random_state=42`  
- Pipeline idempotente  
- Validaciones automáticas  
- Compatible con Python ≥ 3.9  

---

# Decisiones de diseño

| Decisión | Razón |
|---------|--------|
| SQLite | Ligero y portable |
| SQLAlchemy | Evita SQL duro |
| INSERT OR IGNORE | Implementación simple de idempotencia |
| Modularización | Mantención y escalabilidad |
| Manejo suave de errores | Continuidad |

---

# Futuras mejoras

| Mejora | Beneficio |
|--------|-----------|
| PostgreSQL / BigQuery | Escalabilidad |
| Orquestación (Airflow) | Scheduling |

---

# Autoría

**María Javiera Sepúlveda Álamos**  
Ingeniera Civil Industrial  
Santiago – La Serena, Chile  
m.javiera.sepulveda@gmail.com  
[linkedin.com/in/mjavierasa](https://www.linkedin.com/in/mjavierasa)

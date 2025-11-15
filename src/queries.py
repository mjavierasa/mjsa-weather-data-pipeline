"""
Queries: Módulo de consultas del Weather Data Pipeline.

Ejecuta los principales indicadores solicitados sobre la base de datos local `weather_data.db`:

1. Temperatura media observada de la última semana (lunes a domingo)
2. Máximo cambio de velocidad del viento entre observaciones consecutivas (últimos 7 días)
3. Mínima y máxima humedad por día
4. Variación diaria promedio de temperatura y humedad respecto al día anterior

Supuestos:
- La tabla `weather_data` existe y contiene datos válidos obtenidos desde la API del NWS
- Las columnas mantienen la estructura generada por el pipeline principal
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "weather_data.db"


def run_analytics():
    """Ejecuta consultas SQL de análisis sobre los datos almacenados en `weather_data`."""
    print("\n=== Ejecución de análisis sobre datos climáticos ===\n")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # ----------------------------------------------------------------------
        # 1. Temperatura media observada (última semana: lunes a domingo)
        # ----------------------------------------------------------------------
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        last_monday = monday - timedelta(days=7)
        start_date, end_date = last_monday.isoformat(), (monday - timedelta(days=1)).isoformat()

        print("1. Temperatura media observada (última semana: lunes a domingo)")
        query_1 = f"""
            SELECT 
                Nombre_estacion,
                ROUND(AVG(temperatura), 2) AS temperatura_media
            FROM weather_data
            WHERE DATE(hora_observacion) BETWEEN '{start_date}' AND '{end_date}'
              AND temperatura IS NOT NULL
            GROUP BY Nombre_estacion;
        """
        for est, temp in cursor.execute(query_1).fetchall():
            print(f"   - {est}: {temp} °C")

        # ----------------------------------------------------------------------
        # 2. Máximo cambio de velocidad del viento (últimos 7 días)
        # ----------------------------------------------------------------------
        print("\n2. Máximo cambio de velocidad del viento (últimos 7 días)")
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        query_2 = f"""
            WITH cambios AS (
                SELECT 
                    ID_estacion,
                    ABS(velocidad_viento - LAG(velocidad_viento) OVER (
                        PARTITION BY ID_estacion ORDER BY hora_observacion
                    )) AS delta_viento
                FROM weather_data
                WHERE hora_observacion >= '{seven_days_ago}'
                  AND velocidad_viento IS NOT NULL
            )
            SELECT 
                w.Nombre_estacion,
                ROUND(MAX(c.delta_viento), 2) AS max_cambio_viento
            FROM cambios c
            JOIN weather_data w ON c.ID_estacion = w.ID_estacion
            GROUP BY w.Nombre_estacion;
        """
        for est, cambio in cursor.execute(query_2).fetchall():
            print(f"   - {est}: {cambio} m/s")

        # ----------------------------------------------------------------------
        # 3. Mínima y máxima humedad por día
        # ----------------------------------------------------------------------
        print("\n3. Mínima y máxima humedad por día")
        query_3 = """
            SELECT 
                DATE(hora_observacion) AS fecha,
                Nombre_estacion,
                MIN(humedad) AS humedad_min,
                MAX(humedad) AS humedad_max
            FROM weather_data
            WHERE humedad IS NOT NULL
            GROUP BY DATE(hora_observacion), Nombre_estacion
            ORDER BY fecha DESC;
        """
        for fecha, est, hmin, hmax in cursor.execute(query_3).fetchmany(10):
            print(f"   - {fecha} | {est}: Mín {hmin} %, Máx {hmax} %")

        # ----------------------------------------------------------------------
        # 4. Variación diaria promedio de temperatura y humedad (día anterior)
        # ----------------------------------------------------------------------
        print("\n4. Variación diaria promedio de temperatura y humedad (respecto al día anterior)")
        query_4 = """
            WITH promedios_diarios AS (
                SELECT 
                    ID_estacion,
                    Nombre_estacion,
                    DATE(hora_observacion) AS fecha,
                    AVG(temperatura) AS temp_promedio,
                    AVG(humedad) AS hum_promedio
                FROM weather_data
                GROUP BY ID_estacion, DATE(hora_observacion)
            )
            SELECT 
                Nombre_estacion,
                fecha,
                ROUND(temp_promedio - LAG(temp_promedio) OVER (
                    PARTITION BY ID_estacion ORDER BY fecha
                ), 2) AS variacion_temp,
                ROUND(hum_promedio - LAG(hum_promedio) OVER (
                    PARTITION BY ID_estacion ORDER BY fecha
                ), 2) AS variacion_hum
            FROM promedios_diarios
            ORDER BY Nombre_estacion, fecha DESC;
        """
        for est, fecha, vtemp, vhum in cursor.execute(query_4).fetchmany(10):
            if vtemp is not None:
                print(f"   - {est} ({fecha}): ΔTemp {vtemp} °C | ΔHum {vhum} %")

    except sqlite3.Error as e:
        print(f"Error al ejecutar las consultas SQL: {e}")

    finally:
        conn.close()

    print("\nAnálisis completado correctamente.\n")


if __name__ == "__main__":
    run_analytics()

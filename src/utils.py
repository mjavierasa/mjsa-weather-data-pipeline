"""
Utils: Módulo de validaciones básicas del Weather Data Pipeline.

Ejecuta verificaciones preliminares sobre la base de datos SQLite 
para validar la coherencia y completitud de los datos antes de realizar análisis.

Incluye:
1. Temperatura promedio de los últimos 7 días por estación.
2. Total de registros almacenados.
3. Última fecha de observación registrada.

Supuestos:
- La base de datos local es `weather_data.db`.
- La tabla `weather_data` contiene los campos esperados del pipeline.
- Las fechas se almacenan en formato ISO 8601 (UTC).
"""

from sqlalchemy import text
from database import get_engine


def run_basic_validations():
    """Ejecuta validaciones básicas sobre la base de datos SQLite."""
    engine = get_engine()
    with engine.connect() as conn:

        # 1. Temperatura promedio (últimos 7 días)
        q1 = text("""
            SELECT 
                ID_estacion, 
                ROUND(AVG(temperatura), 2) AS temperatura_promedio
            FROM weather_data
            WHERE DATE(hora_observacion) >= DATE('now', '-7 days')
              AND temperatura IS NOT NULL
            GROUP BY ID_estacion
            ORDER BY temperatura_promedio DESC;
        """)
        print("\n1. Temperatura promedio (últimos 7 días):")
        rows = conn.execute(q1).fetchall()
        if rows:
            for row in rows:
                print(f"   - {row[0]}: {row[1]} °C")
        else:
            print("   No se encontraron registros recientes de temperatura.")

        # 2. Total de registros
        q2 = text("SELECT COUNT(*) FROM weather_data;")
        total = conn.execute(q2).scalar()
        print(f"\n2. Total de registros almacenados: {total}")

        # 3. Fecha más reciente
        q3 = text("SELECT MAX(hora_observacion) FROM weather_data;")
        last_date = conn.execute(q3).scalar()
        print(f"\n3. Última fecha de observación registrada: {last_date or 'Sin registros.'}")

    print("\nValidaciones básicas completadas correctamente.\n")


if __name__ == "__main__":
    run_basic_validations()

"""
Archivo Database:conexión y manejo de la base de datos

Incluye funciones para:
- Establecer conexión con el motor de base de datos SQLite.
- Crear tablas dinámicamente a partir del DataFrame de entrada.

Supuestos:
- Se usa una base SQLite local.
- Se define una clave primaria 'unique_key' para asegurar idempotencia.
"""

from sqlalchemy import create_engine, text


def get_engine(db_path="weather_data.db"):
    """Crea y devuelve una conexión al motor SQLite."""
    return create_engine(f"sqlite:///{db_path}")


def create_table(engine, table_name, df):
    """
    Crea la tabla si no existe, basada en las columnas del DataFrame.
    Usa 'unique_key' como clave primaria para evitar duplicados.
    """
    with engine.begin() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                ID_estacion TEXT,
                Nombre_estacion TEXT,
                zona_horaria TEXT,
                latitud REAL,
                longitud REAL,
                hora_observacion TEXT,
                temperatura REAL,
                velocidad_viento REAL,
                humedad REAL,
                unique_key TEXT PRIMARY KEY
            )
        """))

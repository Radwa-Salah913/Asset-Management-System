from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from app.database.models import AssetSource, AssetStatus, AssetType 
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL =os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create Engine only once. 
engine : Engine= create_engine(DB_URL)
def get_engine() -> Engine:
    return engine


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine()
)

# Retrieve the database schema from PostgreSQL and format it as text.
def get_schema():
    inspector_query = text("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position;
    """)
    metadata_keys_query = text("""
        SELECT DISTINCT jsonb_object_keys(metadata_json::jsonb) AS key
        FROM assets
        WHERE metadata_json IS NOT NULL
        ORDER BY key;
    """)

    schema = {}

    try:

        with get_engine().connect() as conn:

            rows = conn.execute(inspector_query).fetchall()
            metadata_keys = [
                row[0]
                for row in conn.execute(metadata_keys_query).fetchall()
            ]
            asset_types = ", ".join(t.value for t in AssetType)
            asset_statuses = ", ".join(s.value for s in AssetStatus)
            asset_sources = ", ".join(s.value for s in AssetSource)

            for table_name, column_name, data_type in rows:

                if table_name not in schema:
                    schema[table_name] = []

                if column_name == "type":
                    schema[table_name].append(
                        f"- {column_name} (enum: {asset_types})"
                    )

                elif column_name == "status":
                    schema[table_name].append(
                        f"- {column_name} (enum: {asset_statuses})"
                    )

                elif column_name == "source":
                    schema[table_name].append(
                        f"- {column_name} (enum: {asset_sources})"
                    )

                elif column_name == "metadata_json":
                    schema[table_name].append(
                        f"- {column_name} ({data_type})"
                    )

                    if metadata_keys:
                        schema[table_name].append(
                            "  Available JSON keys:"
                        )

                        for key in metadata_keys:
                            schema[table_name].append(
                                f"    - {key}"
                            )

                else:
                    schema[table_name].append(
                        f"- {column_name} ({data_type})"
                    )

        schema_text = ""

        for table, columns in schema.items():

            schema_text += f"\nTable: {table}\n"

            schema_text += "\n".join(columns)

            schema_text += "\n"

        return schema_text
    
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve database schema: {e}") from e

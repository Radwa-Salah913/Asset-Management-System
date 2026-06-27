from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL =os.getenv("DATABASE_URL")


def get_engine():
    return create_engine(DB_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_engine()
)

def get_schema():
    inspector_query = text("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position;
    """)

    schema = {}

    with get_engine().connect() as conn:

        rows = conn.execute(inspector_query).fetchall()

        for table_name, column_name, data_type in rows:

            if table_name not in schema:
                schema[table_name] = []

            schema[table_name].append(
                f"- {column_name} ({data_type})"
            )

    schema_text = ""

    for table, columns in schema.items():

        schema_text += f"\nTable: {table}\n"

        schema_text += "\n".join(columns)

        schema_text += "\n"

    return schema_text
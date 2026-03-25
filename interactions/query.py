import logging
import csv
import sys
from sqlalchemy import create_engine, text

from scystream.sdk.env.settings import (
    EnvSettings,
)


def query_db(
    query: str,
    db_settings: EnvSettings,
    output_file_name: str
) -> None:
    try:
        engine = create_engine(db_settings.DB_DSN)
        with engine.connect() as conn:
            result = conn.execute(text(query))
            col_names = result.keys()
            rows = result.fetchall()

            with open(output_file_name, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(col_names)
                writer.writerows(rows)
    except Exception as e:
        logging.error(f"Failed to execute query or write CSV: {e}")
        sys.exit(1)
    finally:
        conn.close()

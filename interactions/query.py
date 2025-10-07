import logging
import psycopg2
import csv
import sys

from scystream.sdk.env.settings import (
    EnvSettings,
)


def query_db(query: str, db_settings: EnvSettings, output_file_name: str) -> None:
    try:
        conn = psycopg2.connect(
            dbname=db_settings.DB_NAME,
            user=db_settings.DB_USER,
            host=db_settings.DB_HOST,
            port=db_settings.DB_PORT
        )
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            col_names = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            with open(output_file_name, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(col_names)
                writer.writerows(rows)

    except Exception as e:
        logging.error(f"Failed to execute query or write CSV: {e}")
        sys.exit(1)
    finally:
        conn.close()

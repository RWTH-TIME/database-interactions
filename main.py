from datetime import datetime
import logging
import sys
import pandas as pd

from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import (
    EnvSettings,
    InputSettings,
    OutputSettings,
    FileSettings,
    DatabaseSettings,
)
from scystream.sdk.database_handling.database_manager import (
    PandasDatabaseOperations,
)
from scystream.sdk.file_handling.s3_manager import S3Operations
from interactions.query import execute_query_to_csv


def upload_to_s3(local_file_path: str, output_settings: FileSettings) -> None:
    try:
        s3_conn = S3Operations(output_settings)
        s3_conn.upload_file(
            path_to_file=local_file_path,
            bucket_name=output_settings.BUCKET_NAME,
            target_name=(
                f"{output_settings.FILE_PATH}/"
                f"{output_settings.FILE_NAME}."
                f"{output_settings.FILE_EXT}"
            ),
        )
    except Exception as e:
        logging.error(f"Failed to upload CSV to S3: {e}")
        sys.exit(1)


def read_query_file(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Failed to read query file: {e}")
        sys.exit(1)


class QueryFileInput(FileSettings, InputSettings):
    __identifier__ = "query_file"


class QueryStrInput(InputSettings):
    QUERY: str = ""


class CSVOutput(FileSettings, OutputSettings):
    __identifier__ = "csv_output"

    FILE_EXT: str = "csv"


class QueryInformationOutput(DatabaseSettings, OutputSettings):
    __identifier__ = "query_information"

    DB_SOURCE_DESCRIPTION: str | None


class QueryDatabaseFromFileEntrypointSettings(EnvSettings):
    DB_DSN: str
    DB_SCHEMA: str | None = None

    query_file: QueryFileInput
    csv_output: CSVOutput
    query_information: QueryInformationOutput


class QueryDatabaseEntrypointSettings(EnvSettings):
    DB_DSN: str
    DB_SCHEMA: str | None = None

    query_str: QueryStrInput
    csv_output: CSVOutput
    query_information: QueryInformationOutput


def write_query_info(query: str, source: str, settings: DatabaseSettings):
    db = PandasDatabaseOperations(settings.DB_DSN, settings.DB_SCHEMA)

    df = pd.DataFrame(
        [{"query": query, "source": source, "created_at": datetime.now()}]
    )

    db.write(table=settings.DB_TABLE, data=df, mode="overwrite")


@entrypoint(QueryDatabaseEntrypointSettings)
def run_query_from_string(settings):
    target_csv = "output.csv"
    execute_query_to_csv(
        query=settings.query_str.QUERY,
        dsn=settings.DB_DSN,
        output_file=target_csv,
        schema=settings.DB_SCHEMA,
    )
    upload_to_s3(target_csv, settings.csv_output)
    write_query_info(
        query=settings.query_str.QUERY,
        source=settings.query_information.DB_SOURCE_DESCRIPTION,
        settings=settings.query_information,
    )


@entrypoint(QueryDatabaseFromFileEntrypointSettings)
def run_query_from_file(settings):
    local_file = "query_file.txt"

    try:
        S3Operations.download(settings.query_file, local_file)
    except Exception as e:
        logging.error(f"Failed to download query file: {e}")
        sys.exit(1)

    query = read_query_file(local_file)
    target_csv = "output.csv"

    execute_query_to_csv(
        query=query,
        dsn=settings.DB_DSN,
        output_file=target_csv,
        schema=settings.DB_SCHEMA,
    )
    upload_to_s3(target_csv, settings.csv_output)
    write_query_info(
        query=query,
        source=settings.query_information.DB_SOURCE_DESCRIPTION,
        settings=settings.query_information,
    )

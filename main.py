import logging
import sys

from scystream.sdk.core import entrypoint
from scystream.sdk.env.settings import (
    EnvSettings,
    InputSettings,
    OutputSettings,
    FileSettings,
)
from scystream.sdk.file_handling.s3_manager import S3Operations
from interactions.query import query_db


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
            )
        )
    except Exception as e:
        logging.error(f"Failed to upload CSV to S3: {e}")
        sys.exit(1)


def read_query_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as f:
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


class QueryDatabaseFromFileEntrypointSettings(EnvSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    query_file: QueryFileInput
    csv_output: CSVOutput


class QueryDatabaseEntrypointSettings(EnvSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    query_str: QueryStrInput
    csv_output: CSVOutput


@entrypoint(QueryDatabaseEntrypointSettings)
def run_query_from_string(settings):
    query = settings.query_str.QUERY
    target_csv = "output.csv"
    query_db(query, settings, target_csv)
    upload_to_s3(target_csv, settings.csv_output)


@entrypoint(QueryDatabaseFromFileEntrypointSettings)
def run_query_from_file(settings):
    local_file = "query_file.txt"

    s3_conn = S3Operations(settings.query_file)
    try:
        s3_conn.download_file(
            bucket_name=settings.query_file.BUCKET_NAME,
            s3_object_name=(
                f"{settings.query_file.FILE_PATH}/"
                f"{settings.query_file.FILE_NAME}."
                f"{settings.query_file.FILE_EXT}"
            ),
            local_file_path=local_file
        )
    except Exception as e:
        logging.error(f"Failed to download query file: {e}")
        sys.exit(1)

    query = read_query_file(local_file)
    target_csv = "output.csv"
    query_db(query, settings, target_csv)
    upload_to_s3(target_csv, settings.csv_output)

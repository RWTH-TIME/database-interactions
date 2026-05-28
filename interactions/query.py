import logging
import sys

import pandas as pd

from scystream.sdk.database_handling.database_manager import (
    PandasDatabaseOperations,
)


def execute_query_to_csv(
    query: str, dsn: str, output_file: str, schema: str | None
) -> pd.DataFrame:
    try:
        db = PandasDatabaseOperations(dsn, schema)
        df = db.read(query=query)
        df.to_csv(output_file, index=False)
        return df
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        sys.exit(1)

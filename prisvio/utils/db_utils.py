
from django.db import connection


def approximate_row_count(table_name: str) -> int:
    """Quick but inacccurate row count for any given table"""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT reltuples FROM pg_class WHERE relname = '{table_name}'")
        row = cursor.fetchone()
    return int(row[0])

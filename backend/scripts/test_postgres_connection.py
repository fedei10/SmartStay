#!/usr/bin/env python3
"""Run the Postgres connection check from app.services.postgres.connection."""

from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.postgres.connection import test_postgres_connection


def main() -> int:
    result = test_postgres_connection()
    print(result)
    return 0 if "Connected" in result else 1


if __name__ == "__main__":
    raise SystemExit(main())

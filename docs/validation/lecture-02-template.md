# Lecture 02 template validation

Tested on Windows 11 with Git 2.45.1.windows.1, CPython 3.12.9, uv 0.7.3,
Polars 1.39.3, Psycopg 3.3.3 (binary), pytest 8.4.2 and PostgreSQL 17.12.

| Check | Observed result |
| --- | --- |
| `uv sync --locked`, Python compile and component imports | Passed |
| `uv run --locked python pipeline.py --help` | Exit 0, month and path options listed |
| `uv run --locked python -m pytest -q` | 5 passed |
| `psql -X -v ON_ERROR_STOP=1 -f sql/init.sql` through uv | Passed on a fresh, disposable database and on an immediate rerun |
| `psql -X -v ON_ERROR_STOP=1 -c "SELECT 1"` through uv | Returned 1 as the non-superuser course database owner |
| `uv run --locked --env-file ../.env -- python -m pytest -q tests/integration` | 1 passed, including column inspection, a scratch insert and rollback |
| `uv run --locked python -m pytest -q tests/acceptance` | Expected exit 1 at the transform TODO |
| `uv run --locked --env-file ../.env -- python pipeline.py` | Expected exit 1 at the extract TODO |
| Lecture verification queries | Executed successfully, trips and zones both empty |

Preflight downloaded the official January 2024 Yellow Taxi Parquet and zone
CSV. Polars inspected the Parquet schema and counted 2,964,624 source rows.
The template leaves data extraction, cleaning and loading for the exercise.

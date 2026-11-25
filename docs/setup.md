# Project setup

You need Git, Python 3.12, uv, a running PostgreSQL server and its `psql`
client. Use a course-owned database separate from other projects and lectures.

## Create a course database

Choose a database role and name. From an administrative `psql` session, the
following example creates a role and a database. The password prompt keeps the
password out of SQL files and shell history.

```sql
CREATE ROLE nibm_etl LOGIN;
\password nibm_etl
CREATE DATABASE nibm_l02 OWNER nibm_etl;
```

If the role already exists, reuse it with a separate database you own. If the
Lecture 02 schema already exists, use the same initialization command below to
ensure both tables exist. The schema is the same on the Lecture 02 template and
complete branches. Git checkout does not switch databases or local data.

## Install the project and initialize the schema

Run from the repository root. Copy the sample configuration and fill in local
connection settings. PowerShell users can use
`Copy-Item .env.example .env` in place of `cp`.

```sh
cp .env.example .env
cd etl
uv sync --locked
cd ..
uv run --no-project --env-file .env -- psql -X -v ON_ERROR_STOP=1 -f sql/init.sql
uv run --no-project --env-file .env -- psql -X -v ON_ERROR_STOP=1 -c "SELECT 1"
```

`uv run --env-file` passes the standard PostgreSQL connection variables to
both Psycopg and `psql`. If your shell already exports a variable such as
`PGDATABASE`, that value takes precedence over the file. Keep the edited
`.env` local. Set `TAXI_DATA_DIR` only if using a separate absolute data directory.

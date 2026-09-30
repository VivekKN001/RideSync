#!/bin/sh
# Passwords from .env, and Grafana's read-only role. Runs on the first start with an empty volume; after
# changing .env (or on a volume from before M9) run it again:
#   docker compose --profile storage exec postgres sh /docker-entrypoint-initdb.d/02_roles.sh
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
     -v owner="$POSTGRES_USER" -v owner_pw="$POSTGRES_PASSWORD" -v grafana_pw="$GRAFANA_DB_PASSWORD" <<'SQL'
ALTER ROLE :"owner" PASSWORD :'owner_pw';
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'grafana') AS missing \gset
\if :missing
CREATE ROLE grafana LOGIN;
\endif
ALTER ROLE grafana PASSWORD :'grafana_pw';
ALTER ROLE grafana SET default_transaction_read_only = on;
ALTER ROLE grafana SET statement_timeout = '30s';
-- A visitor's BEGIN must not leave Grafana's pooled connection stuck in a transaction.
ALTER ROLE grafana SET idle_in_transaction_session_timeout = '5s';
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO grafana;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana;
ALTER DEFAULT PRIVILEGES FOR ROLE :"owner" IN SCHEMA public GRANT SELECT ON TABLES TO grafana;
SQL

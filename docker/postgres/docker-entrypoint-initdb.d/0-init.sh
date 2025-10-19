#!/bin/bash

set -e

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -U "$POSTGRES_USER"; do
  sleep 1;
done

echo "Init script start..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname="postgres"  <<-EOSQL
    ALTER SYSTEM set max_locks_per_transaction = 1024;
    CREATE DATABASE "ci-${POSTGRES_DB}";
EOSQL
echo "Init script end"
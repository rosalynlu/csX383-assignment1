#!/bin/bash

# Load environment variables
source .env

# Create database if it doesn't exist
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true

# Run SQL files
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f schemas/sql/init_schema.sql
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f schemas/sql/seed_data.sql

echo "Database initialized and seeded"

-- scripts/init-db.sql
-- Runs on PostgreSQL container first start
-- Creates the n8n database so n8n can use the same Postgres instance

CREATE DATABASE n8n;
GRANT ALL PRIVILEGES ON DATABASE n8n TO qpilot_user;

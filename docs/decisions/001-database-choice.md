# ADR 001: Database Choice

## Status: Accepted

## Context
The spec requires PostgreSQL (solution spec §22, build spec §8). However, requiring a PostgreSQL install for local development adds friction.

## Decision
- **Development**: SQLite via SQLAlchemy (same ORM, same models)
- **Docker/Production**: PostgreSQL via docker-compose
- **Migrations**: Alembic, works with both backends
- Database URL is configured via `DATABASE_URL` environment variable

## Consequences
- Developers can run the backend locally without PostgreSQL
- JSONB columns use JSON type on SQLite (functionally equivalent for dev)
- Docker Compose deployment uses the spec-required PostgreSQL
- No SQLite-specific features are used; all queries are portable

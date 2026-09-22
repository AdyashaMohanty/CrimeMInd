# CrimeMind Backend — FastAPI + Oracle XE 11g/Oracle Spatial/SDO_GEOMETRY

This is the backend layer for the case-independent CrimeMind frontend. It does not hard-code the Meridian House case. A case reference selects the investigation scope; Oracle XE 11g row-level security is used to prevent cross-case reads after the application migration is installed.

## What is implemented

- FastAPI REST API
- JWT authentication
- investigator registration/login
- case listing/creation
- case assignment
- case-scoped dashboard data
- entities, evidence, communications, transactions, locations, vehicles and relationships
- deterministic query routing
- parameterized execution of CrimeMind SQL modules
- read-only custom SQL mode
- query audit trail
- investigator review/sign-off
- Oracle XE 11g case membership tables
- Oracle XE 11g RLS case isolation
- deterministic advisory synthesis placeholder (AI agent plugs in later)

## Project placement

Copy this `backend` folder into:

    CrimeMind/
      backend/
      database/
      ingestion/
      frontend/
      ...

The backend expects the canonical database SQL modules at:

    ../database/sql_modules

relative to the backend working directory. If your modules are somewhere else, set `SQL_MODULE_DIR` in `.env`.

## Install

From `CrimeMind/backend`:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set the real Oracle XE 11g connection string and a long JWT secret.

## Initialize database

Run from `CrimeMind/backend`:

```powershell
python -m app.cli init-db --schema-dir ../database/ddl
```

If your 18 SQL investigation modules are in `database/sql_modules`, keep `SQL_MODULE_DIR=../database/sql_modules`.

The initializer applies the canonical schema/reference functions that exist in your repo, then the backend application tables and RLS migration. Missing optional SQL files are reported as SKIP rather than silently invented.

## Create the first investigator

```powershell
python -m app.cli create-investigator --name "Demo Investigator" --officer-id DEMO --email demo@example.com --department "Investigation Unit" --password "DEMO12345"
```

Use at least 8 characters. This creates an authorized backend account.

## Case scope for the existing synthetic case

Your current synthetic world is intentionally one investigation. After ingestion has loaded the database and the case row exists, run:

```powershell
python -m app.cli_scope MH-2026-0818
```

This idempotently associates the already-loaded records with that case. For future multi-case ingestion, do not blindly backfill all rows; the ingestion pipeline should explicitly insert the correct `case_*` memberships for each case.

## Run API

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

    http://127.0.0.1:8000/docs

Health:

    http://127.0.0.1:8000/api/health

## Frontend connection

Set the frontend `.env` to:

    VITE_API_BASE_URL=http://127.0.0.1:8000/api

The existing frontend already calls:

- `GET /cases`
- `GET /cases/{case_reference}/dashboard`
- `POST /cases/{case_reference}/queries/run`
- `POST /cases/{case_reference}/reviews`

Authentication should next be switched from the frontend's localStorage prototype to these backend `/auth/register` and `/auth/login` endpoints.

## Query behavior

Natural-language queries are routed to the canonical CrimeMind Q1-Q40 mapping. For the modules currently present in your database directory, the backend loads the SQL file and executes it with named parameters converted safely for Oracle database driver. It never concatenates user values into the SQL.

For Q14-Q40, place the corresponding module files in `SQL_MODULE_DIR`; the router uses the canonical Q-to-module mapping and locates files by their numeric module prefix.

SQL Mode accepts only a single read-only `SELECT`. DDL/DML/multiple statements are rejected. Oracle XE 11g RLS still applies to case-scoped data.

## Security note

This is a capstone-grade backend, not a production law-enforcement deployment. Before production, replace development auto-assignment with explicit case authorization, use a dedicated Oracle XE 11g application role, rotate JWT secrets through a secret manager, enforce HTTPS, add refresh-token/session revocation, rate limiting, structured security logging, and independent security testing.

## Case-driven relationship graph
`GET /api/cases/{case_reference}/relationship-graph` builds the graph from the selected case's Oracle XE 11g records. It includes direct relationships, communications, transactions, entity-vehicle associations, vehicle sightings, evidence links, event-location links, temporal/spatial co-location correlations, and shared-evidence inference. The frontend does not contain a hard-coded relationship list.

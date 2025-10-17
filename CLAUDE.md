# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Casper's Kitchens is a simulated ghost-kitchen food delivery platform demonstrating Databricks capabilities: streaming ingestion, Lakeflow Declarative Pipelines, AI/BI, Agent Bricks, and real-time apps with Lakebase postgres.

The system generates realistic order lifecycle data (creation → kitchen prep → driver delivery → completion) with configurable business parameters and location-specific configurations.

## Architecture

The codebase uses a **stage-based architecture** where each stage is a Databricks notebook orchestrated by the "Casper's Initializer" Lakeflow Job:

- **stages/**: Task notebooks corresponding to job steps in the DAG
- **data/generator/**: Order flow simulators with location-specific JSON configs  
  - **configs/**: Location-specific JSON files defining simulation parameters
- **pipelines/**: Declarative DLT transformations (medallion architecture)
  - **order_items/transformations/**: DLT transformation logic for medallion layers
- **agents/**: ML models and AI agents (refund scoring, complaint handling)
- **apps/**: Databricks applications (refund manager FastAPI app)
- **jobs/**: Streaming job notebooks (refund scoring, complaint processing)
- **utils/uc_state/**: Unity Catalog state management for resource cleanup

## Stage Dependencies (DAG)

```
Raw_Data (required)
  └─> Spark_Declarative_Pipeline (required)
      ├─> Refund_Recommender_Agent
      ├─> Refund_Recommender_Stream
      │   └─> Lakebase_Reverse_ETL
      │       └─> Databricks_App_Refund_Manager
      ├─> Complaint_Agent
      ├─> Complaint_Generator_Stream
      │   └─> Complaint_Agent_Stream
      │       └─> Complaint_Lakebase
```

Only Raw_Data and Spark_Declarative_Pipeline stages are required; others are feature-specific.

## Workflows

### Databricks Bundle Commands

**Deploy to workspace:**
```bash
databricks bundle deploy
```

**Run the Casper's Initializer job:**
```bash
databricks bundle run caspers
```

**Cleanup all resources:**
```bash
databricks bundle run cleanup
```

The bundle is configured in `databricks.yml` with a default `dev` target. Variables can be overridden per target (e.g., `catalog` defaults to `kitchendemo` in bundle but job default is `caspers`).

### Manual Workflow (Alternative)

**Setup:**
1. Run `init.ipynb` in Databricks workspace to create the "Casper's Initializer" job
2. Configure parameters (especially `CATALOG` if name collision exists in metastore)
3. Run the job from Jobs & Pipelines UI (select specific tasks or all)

**Cleanup:**
Run `destroy.ipynb` to remove all resources (uses UC-state tracking)

### Default Job Parameters

- `CATALOG`: `caspers` (must be unique per metastore)
- `SIMULATOR_SCHEMA`: `simulator`
- `EVENTS_VOLUME`: `events`
- `LOCATIONS`: `all` (comma-separated JSON filenames or `all`)
- `LLM_MODEL`: `databricks-meta-llama-3-3-70b-instruct`
- `REFUND_AGENT_ENDPOINT_NAME`: `caspers_refund_agent`
- `COMPLAINT_AGENT_ENDPOINT_NAME`: `caspers_complaint_agent`
- `COMPLAINT_RATE`: `0.15`

## Development Patterns

**Databricks SDK Usage:**
- Notebooks use `databricks-sdk` for programmatic resource creation
- Jobs, pipelines, apps created via SDK return objects
- Use UC-state utility to track resources: `from uc_state import add; add(CATALOG, "jobs", job_obj)`

**Parameter Access:**
- All stage notebooks read parameters via `dbutils.widgets.get("PARAM_NAME")`
- Pass catalog, schema, volume names through job parameters

**Path Resolution:**
- Convert local notebook paths to workspace paths:
  ```python
  abs_path = os.path.abspath("./path/to/notebook")
  dbx_path = abs_path.replace(os.environ.get("DATABRICKS_WORKSPACE_ROOT", "/Workspace"), "/Workspace")
  ```

**DLT (Delta Live Tables) Pipelines:**
- Use `@dlt.table()` decorators in transformation files (see `pipelines/order_items/transformations/transformation.py`)
- Read configs via `spark.conf.get("CONFIG_KEY")`
- Stream with `dlt.read_stream("table_name")` and `.writeStream`
- Medallion pattern: Bronze (raw events) → Silver (normalized) → Gold (aggregates)
- Pipeline definitions automatically detect transformation files via glob patterns

**Resource State Management:**
- Import: `from uc_state import create_state_manager, add`
- Track: `add(catalog, "resource_type", api_response_object)`
- Supported types: `experiments`, `jobs`, `pipelines`, `endpoints`, `apps`, `warehouses`, `databaseinstances`, `databasecatalogs`, `catalogs`
- Cleanup follows deletion order: experiments → jobs → pipelines → endpoints → apps → warehouses → databasecatalogs → catalogs → databaseinstances
- State stored in `{catalog}._internal_state.resources` table

## Data Generator Configuration

**Location configs:** `data/generator/configs/*.json`

Each JSON defines simulation parameters for a ghost kitchen location:
- Simulation window: `start_days_ago`, `end_days_ahead`, `speed_up` (time acceleration multiplier)
- Order volume: `orders_day_1`, `orders_last` (linear growth), `noise_pct`
- Service times: `svc.cs`, `svc.sf`, `svc.fr`, `svc.rp` (Gaussian distributions `[mean, std_dev]`)
- Driver behavior: `driver_arrival` (Beta distribution), `driver_mph`
- Brand dynamics: `brand_momentum`, `momentum_rates`
- Geography: `gk_location` (OSM address), `location_name`, `radius_mi`
- Technical: `batch_rows`, `batch_seconds`, `ping_sec`, `random_seed`

**Event Types Generated:**
`order_created` → `gk_started` → `gk_finished` → `gk_ready` → `driver_arrived` → `driver_picked_up` → `driver_ping` (multiple) → `delivered`

Output: JSON files in `/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/`

## Key Technical Details

**Unity Catalog Structure:**
- Main catalog (default `caspers` for job, `kitchendemo` for bundle) contains all schemas
- `simulator` schema: raw data tables (brands, menus, items, categories) + events volume
- `lakeflow` schema: medallion pipeline tables (all_events, silver_order_items, gold_* tables)
- `_internal_state` schema: resource tracking table (created by uc_state utility)

**Streaming:**
- Raw data uses `spark.readStream.format("cloudFiles")` for volume auto-ingest
- DLT pipelines use continuous mode with watermarks for late data handling
- Complaint/refund streams (in `jobs/`) are Structured Streaming jobs deployed as separate workflow jobs
- Streaming jobs write to Delta tables using `.writeStream.format("delta").outputMode("append")`

**AI Agents:**
- Refund agent: ML model scoring orders for refund eligibility (none/partial/full)
- Complaint agent: UC function-based agent classifying complaints (auto_credit/investigate/escalate)
- Both deployed as model serving endpoints via MLflow
- Agent notebooks in `agents/` create models, stage notebooks deploy to endpoints

**Lakebase Integration:**
- PostgreSQL instances created via `w.database.create_database_instance()`
- Reverse ETL syncs lakehouse tables to postgres for operational queries
- Refund manager app (FastAPI + SQLAlchemy) queries postgres for low-latency reads
- Database catalogs track postgres connection metadata

## Common Workflows

**Adding a New Location:**
1. Copy `data/generator/configs/sanfrancisco.json` as template
2. Update location-specific parameters:
   - `gk_location`: OSM-geocodable address
   - `location_name`: Short identifier for filtering
   - `radius_mi`: Delivery service area
   - Adjust `orders_day_1`, `orders_last`, `speed_up` as needed
3. Run job with `LOCATIONS` parameter set to new filename or `all`
4. See `data/generator/configs/README.md` for full parameter documentation

**Adding a New Stage:**
1. Create notebook in `stages/` directory
2. Add corresponding task to `databricks.yml` under `resources.jobs.caspers.tasks`:
   ```yaml
   - task_key: New_Feature
     depends_on:
       - task_key: Spark_Declarative_Pipeline
     notebook_task:
       notebook_path: ${workspace.root_path}/stages/new_feature
   ```
3. Access parameters via `dbutils.widgets.get("PARAM_NAME")`
4. Track created resources: `add(CATALOG, "resource_type", resource_obj)`

**Testing Pipeline Changes:**
1. Modify transformation in `pipelines/order_items/transformations/transformation.py`
2. Pipeline auto-detects changes via glob pattern
3. Continuous mode pipelines refresh automatically
4. Test locally before deploying with `databricks bundle deploy`

**Extending with New Demo Features:**
- Independent features can be added without DAG dependencies if they consume existing lakeflow tables
- All resources should be tracked via `add(CATALOG, resource_type, obj)` for cleanup
- Follow parameter-passing pattern via job parameters and `dbutils.widgets`
- Use streaming jobs pattern from `jobs/` directory for real-time processing features

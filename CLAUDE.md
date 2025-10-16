# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Casper's Kitchens is a simulated ghost-kitchen food delivery platform demonstrating Databricks capabilities: streaming ingestion, Lakeflow Declarative Pipelines, AI/BI, Agent Bricks, and real-time apps with Lakebase postgres.

The system generates realistic order lifecycle data (creation → kitchen prep → driver delivery → completion) with configurable business parameters and location-specific configurations.

## Architecture

The codebase uses a **stage-based architecture** where each stage is a Databricks notebook orchestrated by the "Casper's Initializer" Lakeflow Job:

- **stages/**: Task notebooks corresponding to job steps in the DAG
- **data/generator/**: Order flow simulators with location-specific JSON configs
- **pipelines/**: Declarative DLT transformations (medallion architecture)
- **agents/**: ML models and AI agents (refund scoring, complaint handling)
- **apps/**: Databricks applications (refund manager FastAPI app)
- **utils/uc_state/**: Unity Catalog state management for resource cleanup

## Stage Dependencies (DAG)

```
Raw_Data (required)
  └─> Lakeflow_Declarative_Pipeline (required)
      ├─> Refund_Recommender_Agent
      ├─> Refund_Recommender_Stream
      │   └─> Lakebase_Reverse_ETL
      │       └─> Databricks_App_Refund_Manager
      ├─> Complaint_Agent
      ├─> Complaint_Generator_Stream
      │   └─> Complaint_Agent_Stream
      │       └─> Complaint_Lakebase
```

Only Raw_Data and Lakeflow stages are required; others are feature-specific.

## Initialization & Workflow

**Setup:**
1. Run `init.ipynb` to create the "Casper's Initializer" job
2. Configure parameters (especially `CATALOG` if name collision exists in metastore)
3. Run the job from Jobs & Pipelines UI (select specific tasks or all)

**Default Parameters:**
- `CATALOG`: `caspers` (must be unique per metastore)
- `SIMULATOR_SCHEMA`: `simulator`
- `EVENTS_VOLUME`: `events`
- `LOCATIONS`: `sanfrancisco.json` (comma-separated list or `all`)
- `LLM_MODEL`: `databricks-meta-llama-3-3-70b-instruct`
- `REFUND_AGENT_ENDPOINT_NAME`: `caspers_refund_agent`
- `COMPLAINT_AGENT_ENDPOINT_NAME`: `caspers_complaint_agent`
- `COMPLAINT_RATE`: `0.15`

**Cleanup:**
Run `destroy.ipynb` to remove all resources (uses UC-state tracking)

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

**Lakeflow Declarative Pipelines:**
- Use `@dlt.table()` decorators in transformation files
- Read configs via `spark.conf.get("CONFIG_KEY")`
- Stream with `dlt.read_stream("table_name")` and `.writeStream`
- Medallion pattern: Bronze (raw events) → Silver (normalized) → Gold (aggregates)

**Resource State Management:**
- Import: `from uc_state import create_state_manager, add`
- Track: `add(catalog, "resource_type", api_response_object)`
- Supported types: `jobs`, `pipelines`, `models`, `apps`, `databaseinstances`, `catalogs`
- Cleanup uses proper deletion order (dependent resources first)

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
- Main catalog (default `caspers`) contains all schemas
- `simulator` schema: raw data tables (brands, menus, items, categories) + events volume
- `lakeflow` schema: medallion pipeline tables (all_events, silver_order_items, gold_* tables)
- `_caspers_state` schema: resource tracking table (created by uc_state utility)

**Streaming:**
- Raw data uses `spark.readStream.format("cloudFiles")` for volume auto-ingest
- Pipelines use DLT streaming with watermarks for late data handling
- Complaint/refund streams process in near real-time

**AI Agents:**
- Refund agent: ML model scoring orders for refund eligibility (none/partial/full)
- Complaint agent: UC function-based agent classifying complaints (auto_credit/investigate/escalate)
- Both deployed as model serving endpoints

**Lakebase Integration:**
- PostgreSQL instances created via `w.database.create_database_instance()`
- Reverse ETL syncs lakehouse tables to postgres for operational queries
- Refund manager app queries postgres via SQLAlchemy

## Common Workflows

**Adding a New Location:**
1. Copy `data/generator/configs/sanfrancisco.json`
2. Update `gk_location`, `location_name`, and desired parameters
3. Set job parameter `LOCATIONS` to include new config filename

**Adding a New Stage:**
1. Create notebook in `stages/` directory
2. Add task to job definition in `init.ipynb` with appropriate `depends_on`
3. Pass required parameters via `base_parameters` in task definition

**Testing Pipeline Changes:**
1. Modify transformation in `pipelines/order_items/transformations/`
2. Pipeline auto-detects changes via glob pattern: `f"{root_dbx_path}/**"`
3. Continuous mode pipelines refresh automatically

**Extending with New Demo Features:**
- Add independent stages that don't require DAG dependencies if they use raw lakeflow tables
- Use `add(CATALOG, resource_type, obj)` to enable cleanup tracking
- Follow parameter-passing pattern via job widgets

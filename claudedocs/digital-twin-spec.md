# Casper's Kitchens Digital Twin Frontend - Technical Specification

**Project Type:** Demo and Visualization Application  
**Primary Focus:** Historical Replay with Real-time Evolution Path  
**Target Audience:** Business Users (Operations, Management, Sales Demos)  
**Deployment:** Databricks App Framework  
**Version:** 1.0  
**Date:** 2025-10-17

---

## Executive Summary

A web-based digital twin frontend that visualizes Casper's Kitchens ghost kitchen operations through historical replay of order lifecycles, delivery routes, and operational metrics. The application enables business users to understand kitchen performance, delivery patterns, and system behavior through an intuitive interface with timeline controls.

**Key Capabilities:**
- Historical replay of order lifecycles with timeline scrubber
- Interactive delivery map showing driver routes and GPS tracking
- Kitchen operations pipeline visualization
- Location switcher for multi-city operations (SF, Chicago, Houston)
- Business KPI dashboard with trend analysis
- Simple 2D visualizations designed for clarity over complexity

---

## Architecture Overview

### Integration with Casper's Platform

```
Spark_Declarative_Pipeline (existing)
  └─> Digital_Twin_App (NEW STAGE)
```

**Stage Definition:**
- Notebook: `stages/digital_twin.ipynb`
- App Directory: `apps/digital-twin/`
- Deployment: Databricks App via `app.yaml`
- Dependencies: Requires lakeflow tables from Spark_Declarative_Pipeline

### Technology Stack

**Backend:**
- FastAPI (Python 3.10+)
- Databricks SQL Connector
- SQLAlchemy for query building
- Server-Sent Events (SSE) for replay streaming

**Frontend:**
- React 18 with TypeScript
- Vite for build tooling
- TanStack Query for data fetching
- Zustand for state management
- Mapbox GL JS for map visualization
- Recharts for charts/graphs
- Tailwind CSS for styling

**Deployment:**
- Databricks Apps framework
- Single-user demo configuration
- No external dependencies beyond Databricks platform

---

## Data Architecture

### Source Tables (Existing in Lakeflow Schema)

**1. `lakeflow.all_events`**
```sql
event_id, event_type, ts, gk_id, location, order_id, sequence, body
```
- Raw event stream from generator
- Contains all order lifecycle events
- Body is JSON string with event-specific data

**2. `lakeflow.silver_order_items`**
```sql
order_id, item_id, quantity, price, brand_id, location, created_at
```
- Normalized order items
- Links orders to brands and menus

**3. `lakeflow.gold_order_summary`**
```sql
order_id, location, created_at, delivered_at, total_duration_min,
kitchen_duration_min, delivery_duration_min, total_amount
```
- Aggregated order metrics
- Pre-calculated durations

**4. `lakeflow.gold_brand_performance`**
```sql
brand_id, location, date, order_count, revenue, avg_delivery_time
```
- Daily brand aggregates

### Backend Data Models

**OrderLifecycle:**
```python
{
  "order_id": "string",
  "location": "string",
  "events": [
    {
      "event_type": "order_created | gk_started | gk_finished | ...",
      "timestamp": "datetime",
      "data": {
        "customer_lat": float,
        "customer_lon": float,
        "items": [...],
        # event-specific fields
      }
    }
  ],
  "total_duration_min": float,
  "status": "completed | in_progress | cancelled"
}
```

**DriverPosition:**
```python
{
  "order_id": "string",
  "timestamp": "datetime",
  "lat": float,
  "lon": float,
  "progress_pct": float,
  "estimated_arrival": "datetime"
}
```

**KitchenMetrics:**
```python
{
  "location": "string",
  "timestamp": "datetime",
  "orders_by_stage": {
    "created": int,
    "cooking": int,
    "ready": int,
    "out_for_delivery": int,
    "completed": int
  },
  "throughput_per_hour": float,
  "avg_service_time_min": float,
  "capacity_utilization_pct": float
}
```

**LocationConfig:**
```python
{
  "location_name": "string",
  "display_name": "string",
  "gk_lat": float,
  "gk_lon": float,
  "radius_mi": float,
  "total_orders": int,
  "date_range": {
    "start": "datetime",
    "end": "datetime"
  }
}
```

---

## API Design

### Backend Endpoints

**Base URL:** `/api/v1`

#### 1. Location Management

**GET `/locations`**
- Returns available locations with metadata
- Response:
```json
{
  "locations": [
    {
      "location_name": "sanfrancisco",
      "display_name": "San Francisco",
      "gk_lat": 37.7749,
      "gk_lon": -122.4194,
      "radius_mi": 4,
      "total_orders": 15234,
      "date_range": {
        "start": "2025-10-14T00:00:00Z",
        "end": "2025-10-17T23:59:59Z"
      }
    }
  ]
}
```

#### 2. Time Range Query

**GET `/locations/{location}/time-range`**
- Query parameters:
  - `start`: ISO datetime
  - `end`: ISO datetime
  - `granularity`: `hour | day | week` (optional)
- Returns aggregated metrics for time range
- Response:
```json
{
  "metrics": {
    "total_orders": 450,
    "avg_delivery_time_min": 32.5,
    "completion_rate_pct": 98.2,
    "total_revenue": 12500.00
  },
  "hourly_breakdown": [
    {
      "timestamp": "2025-10-17T10:00:00Z",
      "order_count": 15,
      "avg_delivery_time": 30.2
    }
  ]
}
```

#### 3. Order Lifecycle

**GET `/orders/{order_id}`**
- Returns complete order lifecycle with all events
- Response:
```json
{
  "order_id": "ord_12345",
  "location": "sanfrancisco",
  "created_at": "2025-10-17T10:15:00Z",
  "delivered_at": "2025-10-17T10:48:00Z",
  "total_duration_min": 33,
  "status": "completed",
  "items": [
    {"item_name": "Burger", "quantity": 2, "brand": "BurgerCo"}
  ],
  "events": [
    {
      "event_type": "order_created",
      "timestamp": "2025-10-17T10:15:00Z",
      "data": {
        "customer_lat": 37.7849,
        "customer_lon": -122.4094
      }
    },
    {
      "event_type": "driver_ping",
      "timestamp": "2025-10-17T10:42:30Z",
      "data": {
        "lat": 37.7799,
        "lon": -122.4144,
        "progress_pct": 65
      }
    }
  ]
}
```

#### 4. Replay Stream

**GET `/locations/{location}/replay`**
- Query parameters:
  - `start`: ISO datetime (required)
  - `end`: ISO datetime (required)
  - `speed`: float multiplier (default: 60x, max: 1000x)
  - `from_time`: ISO datetime (optional, resume playback)
- Server-Sent Events (SSE) stream
- Event types:
  - `order_event`: New order event occurred
  - `metrics_update`: Kitchen/delivery metrics updated
  - `replay_complete`: End of time range reached
  - `replay_position`: Current playback timestamp

**Example SSE Messages:**
```
event: order_event
data: {"order_id": "ord_123", "event_type": "driver_ping", "timestamp": "2025-10-17T10:42:30Z", "data": {...}}

event: metrics_update
data: {"timestamp": "2025-10-17T10:45:00Z", "orders_by_stage": {...}, "throughput": 12.5}

event: replay_position
data: {"current_time": "2025-10-17T10:45:00Z", "progress_pct": 25.5}
```

#### 5. Kitchen Status

**GET `/locations/{location}/kitchen-status`**
- Query parameter: `at_time`: ISO datetime
- Returns snapshot of kitchen state at specific time
- Response:
```json
{
  "timestamp": "2025-10-17T10:45:00Z",
  "orders_by_stage": {
    "created": 3,
    "cooking": 8,
    "ready": 5,
    "out_for_delivery": 12,
    "completed": 432
  },
  "active_orders": [
    {
      "order_id": "ord_123",
      "stage": "cooking",
      "time_in_stage_min": 5.2
    }
  ],
  "capacity_utilization_pct": 72.5
}
```

#### 6. Brand Performance

**GET `/locations/{location}/brands`**
- Query parameters:
  - `start`: ISO datetime
  - `end`: ISO datetime
- Response:
```json
{
  "brands": [
    {
      "brand_id": "brand_1",
      "brand_name": "BurgerCo",
      "order_count": 145,
      "revenue": 3250.00,
      "avg_delivery_time_min": 31.2,
      "trend": "improving"
    }
  ]
}
```

---

## Frontend Architecture

### Component Hierarchy

```
App
├── LocationSelector
├── TimelineControls
│   ├── DateRangePicker
│   ├── PlaybackControls (Play/Pause/Speed)
│   └── TimelineScrubber
├── MainView
│   ├── DeliveryMapPanel
│   │   ├── MapboxMap
│   │   ├── KitchenMarker
│   │   ├── DeliveryRadiusCircle
│   │   ├── ActiveDriverMarkers
│   │   ├── CustomerMarkers
│   │   └── RouteLines
│   ├── KitchenPipelinePanel
│   │   ├── StageCard (Created)
│   │   ├── StageCard (Cooking)
│   │   ├── StageCard (Ready)
│   │   ├── StageCard (Out for Delivery)
│   │   └── FlowIndicators
│   └── MetricsDashboard
│       ├── KPICard (Orders/Hour)
│       ├── KPICard (Avg Delivery Time)
│       ├── KPICard (Completion Rate)
│       ├── TrendChart (Order Volume)
│       └── ServiceTimeChart
└── EventFeed
    └── EventItem (Recent events list)
```

### State Management

**Global State (Zustand):**
```typescript
interface AppState {
  // Location
  selectedLocation: string | null;
  availableLocations: LocationConfig[];
  
  // Timeline
  timeRange: { start: Date; end: Date };
  currentTime: Date;
  isPlaying: boolean;
  playbackSpeed: number;
  
  // Data
  activeOrders: OrderLifecycle[];
  kitchenMetrics: KitchenMetrics;
  recentEvents: OrderEvent[];
  
  // UI
  selectedOrder: string | null;
  mapCenter: [number, number];
  mapZoom: number;
  
  // Actions
  setLocation: (location: string) => void;
  setTimeRange: (start: Date, end: Date) => void;
  setPlaybackSpeed: (speed: number) => void;
  togglePlayback: () => void;
  selectOrder: (orderId: string) => void;
}
```

### Key Frontend Features

#### 1. Timeline Controls

**Features:**
- Date range picker for historical period selection
- Play/Pause/Stop controls
- Speed multiplier slider (1x, 10x, 60x, 100x, 500x, 1000x)
- Progress bar showing current position in time range
- "Jump to interesting moments" presets (peak hours, anomalies)

**Behavior:**
- Play initiates SSE connection to `/replay` endpoint
- Speed changes send new request with updated multiplier
- Pause preserves current position, resume continues from there
- Scrubbing to specific time updates all views to that snapshot

#### 2. Delivery Map

**Features:**
- Mapbox GL JS base map centered on kitchen location
- Kitchen marker (prominent icon at gk_lat/gk_lon)
- Delivery radius circle (transparent overlay)
- Active driver markers (moving dots with ping trails)
- Customer delivery markers (destination pins)
- Route polylines (kitchen → customer with gradient for progress)
- Hover tooltips showing order details

**Behavior:**
- Drivers animate smoothly between ping updates
- Route lines update color based on delivery progress
- Completed deliveries fade out after 30 seconds
- Click order marker → highlight in pipeline + show details
- Map bounds auto-adjust to fit all active deliveries

#### 3. Kitchen Pipeline

**Visual Design:**
- Horizontal flow: Created → Cooking → Ready → Out for Delivery → Completed
- Each stage shows:
  - Stage name and icon
  - Current order count (large number)
  - Avg time in stage
  - Visual "flow" animation between stages
- Color coding:
  - Created: Gray
  - Cooking: Orange
  - Ready: Yellow
  - Out for Delivery: Blue
  - Completed: Green

**Behavior:**
- Click stage → filter map to show only orders in that stage
- Hover order in stage → highlight on map
- Real-time count updates as orders transition

#### 4. Metrics Dashboard

**KPI Cards:**
1. **Orders/Hour**
   - Current throughput
   - Comparison to average (↑ 12% vs avg)
   - Sparkline showing last 6 hours

2. **Avg Delivery Time**
   - Current average
   - Comparison to target (32 min vs 30 min target)
   - Distribution chart (P50, P75, P95)

3. **Completion Rate**
   - Percentage of successful deliveries
   - Comparison to yesterday

4. **Active Orders**
   - Count of in-flight orders
   - Breakdown by stage

**Trend Charts:**
- Order volume over time (line chart)
- Service time distribution by stage (bar chart)
- Brand performance comparison (horizontal bar chart)

#### 5. Event Feed

**Features:**
- Scrollable list of recent events
- Event type icons and color coding
- Timestamp with relative time (e.g., "2 minutes ago")
- Click event → jump to that time in replay

**Event Display:**
```
🆕 Order Created - ord_12345 - 2m ago
   2 items from BurgerCo

🍳 Kitchen Started - ord_12344 - 3m ago
   Cooking 3 items

📦 Ready for Pickup - ord_12343 - 5m ago
   Driver ETA: 2 min

🚗 Driver Ping - ord_12342 - 6m ago
   65% complete, 5 min remaining

✅ Delivered - ord_12341 - 8m ago
   Total time: 32 min
```

---

## User Workflows

### Workflow 1: Initial Demo Load

1. User opens app → lands on welcome screen
2. App fetches available locations → displays location selector
3. User selects "San Francisco"
4. App loads SF configuration and queries available date range
5. Default time range loads (last 24 hours of data)
6. Map centers on SF kitchen, shows radius circle
7. Metrics dashboard shows summary stats for time range
8. Event feed shows recent completed orders

### Workflow 2: Historical Replay

1. User adjusts date range picker to specific day (e.g., Oct 15)
2. User clicks Play button
3. Timeline scrubber starts advancing
4. SSE stream begins sending events at 60x speed
5. Map shows drivers appearing, moving, completing deliveries
6. Kitchen pipeline counts update as orders flow through stages
7. Metrics update in real-time
8. User pauses to examine specific moment
9. User clicks an order on map → sees full lifecycle details
10. User resumes playback or scrubs to different time

### Workflow 3: Location Comparison

1. User selects "Chicago" from location dropdown
2. App resets timeline to Chicago's available date range
3. Map re-centers on Chicago kitchen
4. Metrics refresh to show Chicago data
5. User compares Chicago performance to SF mentally
6. (Future: side-by-side comparison view)

### Workflow 4: Investigating Performance Issue

1. User notices high delivery time in metrics
2. User scrubs timeline to peak hour period
3. User observes many drivers with slow progress on map
4. Kitchen pipeline shows bottleneck at "Ready" stage
5. Event feed shows many "Driver Arrived Late" events
6. User concludes: driver shortage during peak hour
7. User screenshots visualization for operational review

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Backend:**
- [ ] Create `stages/digital_twin.ipynb` deployment notebook
- [ ] Set up FastAPI app structure in `apps/digital-twin/`
- [ ] Implement Databricks SQL connector and connection pooling
- [ ] Create data models for OrderLifecycle, KitchenMetrics, etc.
- [ ] Implement `/locations` endpoint
- [ ] Implement `/locations/{location}/time-range` endpoint
- [ ] Basic error handling and logging

**Frontend:**
- [ ] Initialize React + TypeScript + Vite project
- [ ] Set up Tailwind CSS and base styling
- [ ] Create component structure skeleton
- [ ] Implement LocationSelector component
- [ ] Implement TimelineControls UI (non-functional)
- [ ] Set up Zustand store
- [ ] Implement API client with TanStack Query

**DevOps:**
- [ ] Create `app.yaml` configuration
- [ ] Set up development environment
- [ ] Configure build pipeline

### Phase 2: Core Visualization (Week 3-4)

**Backend:**
- [ ] Implement `/orders/{order_id}` endpoint
- [ ] Implement `/locations/{location}/kitchen-status` endpoint
- [ ] Build SSE `/replay` endpoint with time-based event streaming
- [ ] Optimize queries with appropriate indexes
- [ ] Add caching layer for frequently accessed data

**Frontend:**
- [ ] Integrate Mapbox GL JS
- [ ] Implement DeliveryMapPanel with kitchen marker
- [ ] Add delivery radius circle overlay
- [ ] Implement driver markers with animation
- [ ] Add route polylines
- [ ] Implement KitchenPipelinePanel with stage cards
- [ ] Create MetricsDashboard with KPI cards
- [ ] Connect all components to Zustand state

### Phase 3: Replay & Interactivity (Week 5-6)

**Backend:**
- [ ] Implement playback speed controls in SSE stream
- [ ] Add resume functionality (from_time parameter)
- [ ] Implement `/locations/{location}/brands` endpoint
- [ ] Performance optimization for high-speed replay
- [ ] Add data validation and error responses

**Frontend:**
- [ ] Implement SSE client for replay stream
- [ ] Connect play/pause/stop controls
- [ ] Implement speed multiplier slider
- [ ] Add timeline scrubber with seek functionality
- [ ] Implement smooth driver animation between pings
- [ ] Add EventFeed component with scrolling
- [ ] Implement order selection and detail modal
- [ ] Add "jump to interesting moments" feature

### Phase 4: Polish & Demo Prep (Week 7)

**Backend:**
- [ ] Add comprehensive logging and monitoring
- [ ] Performance profiling and optimization
- [ ] Documentation of API endpoints
- [ ] Health check endpoints

**Frontend:**
- [ ] Responsive design refinements
- [ ] Loading states and error handling
- [ ] Empty states for no data
- [ ] Tooltips and user guidance
- [ ] Performance optimization (memoization, virtualization)
- [ ] Keyboard shortcuts
- [ ] Visual polish and animations

**Testing & Documentation:**
- [ ] Integration testing with real data
- [ ] User acceptance testing with business users
- [ ] Create demo script and talking points
- [ ] Record demo video
- [ ] Write user documentation

---

## Database Query Patterns

### Example Queries

**1. Get All Events for Time Range:**
```sql
SELECT 
  event_id, 
  event_type, 
  ts, 
  order_id, 
  body
FROM lakeflow.all_events
WHERE location = :location
  AND ts BETWEEN :start_time AND :end_time
ORDER BY ts ASC
```

**2. Kitchen Status at Time:**
```sql
WITH latest_events AS (
  SELECT 
    order_id,
    event_type,
    ts,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY ts DESC) as rn
  FROM lakeflow.all_events
  WHERE location = :location
    AND ts <= :at_time
)
SELECT 
  CASE 
    WHEN event_type IN ('order_created') THEN 'created'
    WHEN event_type IN ('gk_started') THEN 'cooking'
    WHEN event_type IN ('gk_finished', 'gk_ready') THEN 'ready'
    WHEN event_type IN ('driver_picked_up', 'driver_ping') THEN 'out_for_delivery'
    WHEN event_type IN ('delivered') THEN 'completed'
  END as stage,
  COUNT(*) as order_count
FROM latest_events
WHERE rn = 1
GROUP BY stage
```

**3. Active Drivers at Time:**
```sql
WITH latest_pings AS (
  SELECT 
    order_id,
    ts,
    body,
    ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY ts DESC) as rn
  FROM lakeflow.all_events
  WHERE location = :location
    AND event_type = 'driver_ping'
    AND ts <= :at_time
)
SELECT 
  order_id,
  ts as last_ping_time,
  JSON_EXTRACT_SCALAR(body, '$.lat') as lat,
  JSON_EXTRACT_SCALAR(body, '$.lon') as lon,
  JSON_EXTRACT_SCALAR(body, '$.progress_pct') as progress_pct
FROM latest_pings
WHERE rn = 1
  AND ts > :at_time - INTERVAL 5 MINUTE
```

---

## Configuration & Deployment

### App Configuration (`apps/digital-twin/app.yaml`)

```yaml
name: caspers-digital-twin
description: Digital twin frontend for ghost kitchen visualization

command:
  - "uvicorn"
  - "app.main:app"
  - "--host"
  - "0.0.0.0"
  - "--port"
  - "8000"

resources:
  - name: main
    serving:
      min_replicas: 1
      max_replicas: 1

env:
  - name: CATALOG
    value: ${var.catalog}
  - name: SIMULATOR_SCHEMA
    value: simulator
  - name: LAKEFLOW_SCHEMA
    value: lakeflow
```

### Stage Notebook (`stages/digital_twin.ipynb`)

```python
# Cell 1: Get parameters
CATALOG = dbutils.widgets.get("CATALOG")

# Cell 2: Import dependencies
from databricks.sdk import WorkspaceClient
from uc_state import add
import os

w = WorkspaceClient()

# Cell 3: Get workspace path
abs_path = os.path.abspath("../apps/digital-twin")
app_path = abs_path.replace(
    os.environ.get("DATABRICKS_WORKSPACE_ROOT", "/Workspace"), 
    "/Workspace"
)

# Cell 4: Create/update app
app = w.apps.create(
    name="caspers-digital-twin",
    description="Digital twin frontend for ghost kitchen visualization"
)

# Cell 5: Track in UC state
add(CATALOG, "apps", app)

print(f"Digital twin app deployed: {app.name}")
print(f"URL: {app.url}")
```

### Databricks Bundle Update (`databricks.yml`)

```yaml
resources:
  jobs:
    caspers:
      tasks:
        # ... existing tasks ...
        
        - task_key: Digital_Twin_App
          depends_on:
            - task_key: Spark_Declarative_Pipeline
          notebook_task:
            notebook_path: ${workspace.root_path}/stages/digital_twin
```

---

## Performance Considerations

### Backend Optimization

1. **Query Optimization:**
   - Index on (location, ts) for time-range queries
   - Partition tables by location and date
   - Use Delta caching for frequently accessed data

2. **SSE Stream Efficiency:**
   - Batch events every 100ms for high-speed replay
   - Implement backpressure if client can't keep up
   - Limit active connections to 1 (demo constraint)

3. **Caching Strategy:**
   - Cache location metadata (15 min TTL)
   - Cache aggregated metrics (5 min TTL)
   - No caching for event streams (real-time data)

### Frontend Optimization

1. **Map Performance:**
   - Cluster markers when >50 active deliveries
   - Use WebGL rendering for animations
   - Debounce map updates during high-speed replay

2. **State Management:**
   - Memo expensive calculations (route distances, aggregations)
   - Virtual scrolling for event feed (>100 events)
   - Throttle chart updates to 2 FPS during fast replay

3. **Bundle Size:**
   - Code splitting by route (future)
   - Lazy load Mapbox only when needed
   - Tree-shake unused chart types

---

## Testing Strategy

### Backend Testing

1. **Unit Tests:**
   - Data model serialization/deserialization
   - Query builder functions
   - SSE event formatting

2. **Integration Tests:**
   - API endpoints with test database
   - SSE stream with mock events
   - Error handling scenarios

3. **Performance Tests:**
   - Load test with 1000x speed replay
   - Memory usage over 1-hour replay
   - Query latency for large time ranges

### Frontend Testing

1. **Component Tests:**
   - Render all components in isolation
   - User interactions (click, hover, drag)
   - State updates and re-renders

2. **Integration Tests:**
   - Complete replay workflow
   - Location switching
   - Timeline scrubbing

3. **E2E Tests (with Playwright):**
   - Full demo flow: load → select location → replay → pause → scrub
   - Map interactions and order selection
   - Error states and recovery

---

## Future Enhancements (Post-MVP)

### Phase 2 Features

1. **Multi-Location Comparison View:**
   - Side-by-side maps for 2+ locations
   - Normalized metrics comparison
   - "Race" mode showing which location performs better

2. **3D Kitchen Visualization:**
   - Three.js 3D model of kitchen layout
   - Spatial view of orders at different stations
   - Camera controls for exploration

3. **Advanced Analytics:**
   - Predictive modeling (forecasted order volume)
   - Anomaly detection with alerts
   - What-if scenario builder

4. **Real-Time Mode:**
   - WebSocket connection to live data stream
   - Auto-refresh when new data arrives
   - "Jump to live" button from historical replay

5. **Export & Sharing:**
   - Export replay as video
   - Share specific time ranges via URL
   - Screenshot with annotations

6. **Mobile Responsive:**
   - Touch-optimized timeline controls
   - Simplified mobile view
   - Progressive Web App (PWA) support

### Technical Debt & Improvements

- Add authentication/authorization (if multi-user)
- Implement proper logging and observability
- Add telemetry for usage analytics
- Improve error messages and user feedback
- Internationalization (i18n) support
- Accessibility (WCAG 2.1 AA compliance)

---

## Success Metrics

### Demo Effectiveness
- Time to first insight: <30 seconds from app load
- Comprehension rate: >90% of viewers understand kitchen flow
- Engagement: Viewers actively explore timeline/map

### Technical Performance
- Page load time: <3 seconds
- Replay startup latency: <1 second
- Smooth animation: 30+ FPS during replay
- SSE stream stability: No dropped events at 60x speed

### Business Impact
- Demo conversion: Increased interest in Databricks capabilities
- Internal adoption: Used in 5+ customer demos
- Feature requests: Feedback leads to Phase 2 prioritization

---

## Appendix

### Glossary

- **Digital Twin:** Virtual representation of physical system mirroring real-time or historical state
- **Order Lifecycle:** Complete journey from order creation to delivery
- **Replay:** Playing back historical data with time controls
- **SSE (Server-Sent Events):** HTTP-based server-to-client streaming protocol
- **Medallion Architecture:** Bronze (raw) → Silver (cleaned) → Gold (aggregated) data pattern
- **DLT (Delta Live Tables):** Databricks declarative pipeline framework

### References

- Casper's Kitchens main documentation: `/README.md`
- Data generator configuration: `/data/generator/configs/README.md`
- Existing app example: `/apps/refund-manager/`
- Databricks Apps documentation: https://docs.databricks.com/en/dev-tools/databricks-apps/

### Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-17 | Initial specification based on requirements discovery |

---

**Specification Status:** READY FOR DEVELOPMENT  
**Next Steps:** Review and approval → Begin Phase 1 implementation

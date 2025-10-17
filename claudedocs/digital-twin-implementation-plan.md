# Digital Twin Implementation Plan - Detailed Phased Approach

**Project:** Casper's Kitchens Digital Twin Frontend  
**Total Duration:** 7 weeks  
**Team Size:** 1-2 developers  
**Version:** 1.0  
**Date:** 2025-10-17

---

## Overview

This implementation plan breaks down the digital twin development into 4 sequential phases, each with clear deliverables and acceptance criteria. Each phase builds on the previous, allowing for early testing and feedback.

**Phase Timeline:**

- Phase 1: Foundation (2 weeks)
- Phase 2: Core Visualization (2 weeks)
- Phase 3: Replay & Interactivity (2 weeks)
- Phase 4: Polish & Demo Prep (1 week)

---

## Phase 1: Foundation (Weeks 1-2)

**Goal:** Establish project structure, data connectivity, and basic UI framework

**Duration:** 2 weeks (80 hours)

**Deliverables:**

- Working FastAPI backend with database connectivity
- React frontend scaffold with routing
- Location selector with real data
- Basic API endpoints functional
- Deployment configuration complete

### Week 1: Backend Foundation

#### Day 1-2: Project Setup & Structure

**Tasks:**

1. **Create directory structure**
   - [ ] Create `apps/digital-twin/` directory
   - [ ] Create subdirectories: `app/`, `app/api/`, `app/models/`, `app/services/`
   - [ ] Create `app/static/` for frontend build output
   - [ ] Create `tests/` directory with `test_api.py`, `test_models.py`

2. **Initialize Python project**
   - [ ] Create `requirements.txt` with dependencies:
     - fastapi==0.104.1
     - uvicorn==0.24.0
     - databricks-sql-connector==3.0.0
     - sqlalchemy==2.0.23
     - pydantic==2.5.0
     - python-dotenv==1.0.0
   - [ ] Create `app/__init__.py` package files
   - [ ] Create `.env.example` for configuration template

3. **Set up FastAPI application**
   - [ ] Create `app/main.py` with FastAPI app initialization
   - [ ] Add CORS middleware for frontend communication
   - [ ] Add health check endpoint: `GET /health`
   - [ ] Add root endpoint: `GET /` serving frontend static files
   - [ ] Test app starts successfully with `uvicorn app.main:app --reload`

**Acceptance Criteria:**

- FastAPI server starts on port 8000
- `/health` endpoint returns 200 OK
- Project structure matches specification

#### Day 3-4: Database Connectivity

**Tasks:**

1. **Configure Databricks SQL connection**
   - [ ] Create `app/config.py` for environment variables
   - [ ] Read CATALOG, SIMULATOR_SCHEMA, LAKEFLOW_SCHEMA from env
   - [ ] Create `app/db.py` with connection factory function
   - [ ] Implement connection pooling (max 5 connections)
   - [ ] Add connection retry logic with exponential backoff

2. **Create data models**
   - [ ] Create `app/models/location.py` - LocationConfig model
   - [ ] Create `app/models/order.py` - OrderLifecycle, OrderEvent models
   - [ ] Create `app/models/metrics.py` - KitchenMetrics model
   - [ ] Create `app/models/driver.py` - DriverPosition model
   - [ ] Add Pydantic validators for data integrity

3. **Test database queries**
   - [ ] Write test query to fetch locations from lakeflow.all_events
   - [ ] Write test query to count orders by location
   - [ ] Verify connection to actual Casper's data
   - [ ] Add logging for query execution times

**Acceptance Criteria:**

- Database connection successful
- Can query lakeflow tables
- Models serialize/deserialize correctly
- Connection pool handles concurrent requests

#### Day 5: Location Management API

**Tasks:**

1. **Implement location service**
   - [ ] Create `app/services/location_service.py`
   - [ ] Implement `get_available_locations()` function
   - [ ] Query distinct locations from lakeflow.all_events
   - [ ] Extract location metadata (gk coordinates, radius from generator configs)
   - [ ] Calculate order counts and date ranges per location

2. **Create location endpoints**
   - [ ] Create `app/api/locations.py` router
   - [ ] Implement `GET /api/v1/locations` endpoint
   - [ ] Add response model with LocationConfig list
   - [ ] Add error handling for database errors
   - [ ] Add request logging

3. **Write tests**
   - [ ] Create `tests/test_locations.py`
   - [ ] Test locations endpoint returns valid data
   - [ ] Test error handling for database failures
   - [ ] Test response schema validation

**Acceptance Criteria:**

- `GET /api/v1/locations` returns list of locations
- Response includes SF, Chicago, Houston (if data exists)
- Each location has valid coordinates and metadata
- Tests pass with >80% coverage

### Week 2: Frontend Foundation

#### Day 1-2: React Project Setup

**Tasks:**

1. **Initialize React project**
   - [ ] Run `npm create vite@latest frontend -- --template react-ts`
   - [ ] Move frontend into `apps/digital-twin/frontend/`
   - [ ] Install dependencies: react-router-dom, @tanstack/react-query, zustand
   - [ ] Install UI dependencies: tailwindcss, @headlessui/react, lucide-react
   - [ ] Configure Tailwind CSS with custom theme

2. **Set up project structure**
   - [ ] Create `src/components/` directory with subdirs:
     - `layout/` - App shell, navigation
     - `timeline/` - Timeline controls
     - `map/` - Map components
     - `kitchen/` - Kitchen pipeline
     - `metrics/` - Dashboard components
     - `common/` - Shared components (buttons, cards, etc.)
   - [ ] Create `src/hooks/` for custom React hooks
   - [ ] Create `src/services/` for API client
   - [ ] Create `src/store/` for Zustand store
   - [ ] Create `src/types/` for TypeScript interfaces

3. **Configure build and dev**
   - [ ] Update `vite.config.ts` to proxy API requests to backend
   - [ ] Configure build output to `../app/static/`
   - [ ] Set up hot module replacement for development
   - [ ] Add scripts to `package.json`: dev, build, preview

**Acceptance Criteria:**

- React dev server starts on port 5173
- Tailwind CSS styling works
- API proxy forwards requests to backend
- Build outputs to correct directory

#### Day 3: API Client & State Management

**Tasks:**

1. **Create API client**
   - [ ] Create `src/services/api.ts` with base configuration
   - [ ] Implement `fetchLocations()` function
   - [ ] Add error handling and retry logic
   - [ ] Configure axios/fetch with base URL and headers

2. **Set up TanStack Query**
   - [ ] Create `src/services/queryClient.ts`
   - [ ] Configure QueryClient with default options
   - [ ] Create `src/hooks/useLocations.ts` custom hook
   - [ ] Add loading and error states

3. **Implement Zustand store**
   - [ ] Create `src/store/appStore.ts`
   - [ ] Define state interface matching specification
   - [ ] Implement actions: setLocation, setTimeRange, etc.
   - [ ] Add persistence middleware for selected location
   - [ ] Create selectors for derived state

4. **Create TypeScript types**
   - [ ] Create `src/types/location.ts` matching backend models
   - [ ] Create `src/types/order.ts`
   - [ ] Create `src/types/metrics.ts`
   - [ ] Create `src/types/ui.ts` for UI-specific state

**Acceptance Criteria:**

- API client successfully calls backend
- TanStack Query fetches and caches data
- Zustand store updates trigger re-renders
- TypeScript types match backend schemas

#### Day 4-5: Core UI Components

**Tasks:**

1. **Create layout components**
   - [ ] Create `src/components/layout/AppLayout.tsx`
     - Header with app title and logo
     - Main content area
     - Footer with status bar
   - [ ] Create `src/components/layout/Header.tsx`
   - [ ] Create responsive layout grid

2. **Build LocationSelector component**
   - [ ] Create `src/components/common/LocationSelector.tsx`
   - [ ] Use Headless UI Listbox for dropdown
   - [ ] Display location name and order count
   - [ ] Connect to Zustand store for selection
   - [ ] Show loading spinner while fetching locations
   - [ ] Handle empty state (no locations available)

3. **Create timeline UI skeleton**
   - [ ] Create `src/components/timeline/TimelineControls.tsx`
   - [ ] Create `src/components/timeline/DateRangePicker.tsx` (stub)
   - [ ] Create `src/components/timeline/PlaybackControls.tsx` (stub)
   - [ ] Create `src/components/timeline/TimelineScrubber.tsx` (stub)
   - [ ] Layout components in header area (non-functional)

4. **Build main view skeleton**
   - [ ] Create `src/components/MainView.tsx` with 3-panel layout
   - [ ] Create placeholder for map panel (left 60%)
   - [ ] Create placeholder for kitchen panel (right 40% top)
   - [ ] Create placeholder for metrics panel (right 40% bottom)
   - [ ] Add panel resize handles (future enhancement)

5. **Add common components**
   - [ ] Create `src/components/common/Button.tsx` with variants
   - [ ] Create `src/components/common/Card.tsx`
   - [ ] Create `src/components/common/LoadingSpinner.tsx`
   - [ ] Create `src/components/common/ErrorMessage.tsx`

**Acceptance Criteria:**

- Location selector shows real locations from API
- Can select location and see selection in UI
- Layout is responsive and panels are positioned correctly
- All components follow Tailwind CSS styling
- TypeScript types are properly enforced

### Phase 1 Integration & Testing

**Tasks:**

1. **Integration testing**
   - [ ] Test full flow: start backend → start frontend → select location
   - [ ] Verify API calls succeed with real database
   - [ ] Test error handling (disconnect database, break API)
   - [ ] Check browser console for errors

2. **Code quality**
   - [ ] Run ESLint on frontend code
   - [ ] Run mypy/pylint on backend code
   - [ ] Fix all linting errors
   - [ ] Add missing type hints

3. **Documentation**
   - [ ] Update README with setup instructions
   - [ ] Document environment variables required
   - [ ] Add API endpoint documentation with examples
   - [ ] Create development workflow guide

**Phase 1 Deliverables:**

- ✅ Backend API serving location data
- ✅ Frontend with location selector functional
- ✅ Database connectivity working
- ✅ Project structure complete
- ✅ Development environment documented

**Phase 1 Exit Criteria:**

- All tests pass
- Location selector works end-to-end
- Code is linted and type-checked
- Documentation is complete
- Ready for Phase 2 visualization work

---

## Phase 2: Core Visualization (Weeks 3-4)

**Goal:** Implement map, kitchen pipeline, and metrics dashboard with static data views

**Duration:** 2 weeks (80 hours)

**Deliverables:**

- Interactive map showing kitchen and delivery area
- Kitchen pipeline visualization with stage counts
- Metrics dashboard with KPIs
- Time range query working
- All visualizations connected to real data

### Week 3: Map Implementation

#### Day 1-2: Mapbox Integration

**Tasks:**

1. **Set up Mapbox**
   - [ ] Install mapbox-gl: `npm install mapbox-gl @types/mapbox-gl`
   - [ ] Add Mapbox access token to environment variables
   - [ ] Create `src/components/map/MapContainer.tsx`
   - [ ] Initialize Mapbox map centered on selected location
   - [ ] Configure map style (streets, satellite, or custom)
   - [ ] Add zoom controls and navigation controls

2. **Implement kitchen marker**
   - [ ] Create `src/components/map/KitchenMarker.tsx`
   - [ ] Add custom icon for kitchen location
   - [ ] Position marker at gk_lat/gk_lon
   - [ ] Add popup with kitchen details on click
   - [ ] Style marker to stand out (larger, distinct color)

3. **Add delivery radius**
   - [ ] Create `src/components/map/DeliveryRadius.tsx`
   - [ ] Draw circle overlay using Mapbox circle layer
   - [ ] Set radius from location config (miles → meters conversion)
   - [ ] Style with semi-transparent fill and dashed border
   - [ ] Toggle visibility with UI control

**Acceptance Criteria:**

- Map loads and displays correctly
- Kitchen marker appears at correct coordinates
- Delivery radius circle shows accurate area
- Map is interactive (pan, zoom)

#### Day 3-4: Backend Order Endpoints

**Tasks:**

1. **Implement time-range service**
   - [ ] Create `app/services/order_service.py`
   - [ ] Implement `get_orders_in_range(location, start, end)` function
   - [ ] Query lakeflow.all_events with time filter
   - [ ] Group events by order_id
   - [ ] Parse JSON body fields for lat/lon data
   - [ ] Calculate order statistics (count, avg duration)

2. **Create time-range endpoint**
   - [ ] Create `app/api/orders.py` router
   - [ ] Implement `GET /api/v1/locations/{location}/time-range`
   - [ ] Add query parameters: start, end, granularity
   - [ ] Return metrics summary and hourly breakdown
   - [ ] Add caching with 5-minute TTL
   - [ ] Optimize query with indexes if slow

3. **Implement order detail endpoint**
   - [ ] Implement `GET /api/v1/orders/{order_id}`
   - [ ] Fetch all events for specific order
   - [ ] Parse and structure event data
   - [ ] Calculate order metrics (durations, status)
   - [ ] Join with silver_order_items for order details

**Acceptance Criteria:**

- Time-range endpoint returns aggregated metrics
- Order detail endpoint returns full lifecycle
- Queries execute in <2 seconds
- Data matches what's in lakeflow tables

#### Day 5: Order Visualization on Map

**Tasks:**

1. **Implement customer markers**
   - [ ] Create `src/components/map/CustomerMarkers.tsx`
   - [ ] Fetch orders for current time range
   - [ ] Extract delivery coordinates from order events
   - [ ] Add markers for each customer location
   - [ ] Color-code by order status (in-progress, completed)
   - [ ] Add tooltips with order details

2. **Implement route lines**
   - [ ] Create `src/components/map/RouteLines.tsx`
   - [ ] Draw polylines from kitchen to customer
   - [ ] Use route data from driver_picked_up event body
   - [ ] Style with gradient (kitchen=green, customer=blue)
   - [ ] Show only active/recent deliveries (last hour)

3. **Add map interactions**
   - [ ] Click customer marker → show order details modal
   - [ ] Hover marker → show order ID and status
   - [ ] Click route line → highlight order in other panels
   - [ ] Fit map bounds to show all markers

**Acceptance Criteria:**

- Customer markers appear at correct locations
- Routes display for delivered orders
- Click interactions work correctly
- Map performance is smooth with 50+ markers

### Week 4: Kitchen Pipeline & Metrics

#### Day 1-2: Kitchen Status Backend

**Tasks:**

1. **Implement kitchen status service**
   - [ ] Add `get_kitchen_status(location, at_time)` to order_service.py
   - [ ] Query latest event per order before at_time
   - [ ] Group orders by stage (created, cooking, ready, etc.)
   - [ ] Calculate time spent in each stage
   - [ ] Return active order IDs per stage

2. **Create kitchen status endpoint**
   - [ ] Implement `GET /api/v1/locations/{location}/kitchen-status`
   - [ ] Query parameter: `at_time` (ISO datetime)
   - [ ] Return orders_by_stage counts
   - [ ] Return list of active orders with details
   - [ ] Add caching for historical queries

3. **Optimize kitchen status query**
   - [ ] Review SQL execution plan
   - [ ] Add indexes if needed (location, ts, order_id)
   - [ ] Use window functions for latest event per order
   - [ ] Test with large datasets (10k+ orders)

**Acceptance Criteria:**

- Kitchen status endpoint returns correct stage counts
- Query executes in <1 second
- Active orders include stage and timing info
- Caching reduces load on database

#### Day 3: Kitchen Pipeline UI

**Tasks:**

1. **Create kitchen pipeline component**
   - [ ] Create `src/components/kitchen/KitchenPipeline.tsx`
   - [ ] Create `src/components/kitchen/StageCard.tsx`
   - [ ] Layout 5 stages horizontally with arrows
   - [ ] Display stage name, icon, and order count
   - [ ] Color-code stages (gray, orange, yellow, blue, green)

2. **Add flow animations**
   - [ ] Animate order count changes with number transitions
   - [ ] Add pulse effect when orders move between stages
   - [ ] Use Framer Motion or CSS transitions
   - [ ] Add arrow animations showing flow direction

3. **Connect to API**
   - [ ] Create `src/hooks/useKitchenStatus.ts`
   - [ ] Fetch kitchen status for current time
   - [ ] Update every 5 seconds (for future real-time mode)
   - [ ] Display loading state while fetching

4. **Add interactions**
   - [ ] Click stage → filter map to show orders in that stage
   - [ ] Hover stage → show tooltip with avg time in stage
   - [ ] Show/hide completed orders toggle

**Acceptance Criteria:**

- Pipeline displays all 5 stages correctly
- Order counts update from API data
- Animations are smooth and not distracting
- Click interactions work as specified

#### Day 4-5: Metrics Dashboard

**Tasks:**

1. **Create KPI card component**
   - [ ] Create `src/components/metrics/KPICard.tsx`
   - [ ] Props: title, value, comparison, trend, sparkline data
   - [ ] Display large value with unit
   - [ ] Show comparison indicator (↑ 12% vs avg)
   - [ ] Add mini sparkline chart

2. **Implement metrics service**
   - [ ] Add `get_metrics_summary(location, start, end)` to order_service
   - [ ] Calculate orders/hour average
   - [ ] Calculate avg delivery time from gold_order_summary
   - [ ] Calculate completion rate (delivered / total)
   - [ ] Query hourly order counts for sparklines

3. **Build metrics dashboard**
   - [ ] Create `src/components/metrics/MetricsDashboard.tsx`
   - [ ] Create 4 KPI cards: Orders/Hour, Avg Delivery Time, Completion Rate, Active Orders
   - [ ] Fetch metrics for current time range
   - [ ] Update when time range changes

4. **Add trend charts**
   - [ ] Install Recharts: `npm install recharts`
   - [ ] Create `src/components/metrics/OrderVolumeChart.tsx`
   - [ ] Display line chart of orders over time
   - [ ] Create `src/components/metrics/ServiceTimeChart.tsx`
   - [ ] Display bar chart of service times by stage
   - [ ] Style charts to match app theme

**Acceptance Criteria:**

- All 4 KPI cards display accurate metrics
- Sparklines show hourly trends
- Trend charts render with real data
- Charts are responsive and legible

### Phase 2 Integration & Testing

**Tasks:**

1. **End-to-end testing**
   - [ ] Test complete flow: select location → view map → view pipeline → view metrics
   - [ ] Verify all data matches between components
   - [ ] Test with different locations (SF, Chicago)
   - [ ] Test with different time ranges

2. **Performance testing**
   - [ ] Measure page load time (<3s target)
   - [ ] Profile React render performance
   - [ ] Optimize slow queries
   - [ ] Add loading skeletons for slow components

3. **Accessibility**
   - [ ] Add ARIA labels to interactive elements
   - [ ] Ensure keyboard navigation works
   - [ ] Test with screen reader (basic)
   - [ ] Fix contrast issues

**Phase 2 Deliverables:**

- ✅ Interactive map with kitchen, customers, routes
- ✅ Kitchen pipeline showing order flow
- ✅ Metrics dashboard with KPIs and charts
- ✅ All components connected to real data
- ✅ Time range selector functional

**Phase 2 Exit Criteria:**

- All visualizations display correct data
- No critical performance issues
- Code is tested and linted
- Ready for Phase 3 replay functionality

---

## Phase 3: Replay & Interactivity (Weeks 5-6)

**Goal:** Implement historical replay with timeline controls and SSE streaming

**Duration:** 2 weeks (80 hours)

**Deliverables:**

- Timeline controls with play/pause/speed
- SSE streaming for event replay
- Animated driver movement
- Event feed with recent events
- Order detail modal
- Full replay functionality

### Week 5: Timeline Controls & Backend Streaming

#### Day 1-2: Timeline UI Components

**Tasks:**

1. **Build date range picker**
   - [ ] Install date picker library: `npm install react-datepicker`
   - [ ] Create `src/components/timeline/DateRangePicker.tsx`
   - [ ] Show start and end date inputs
   - [ ] Validate end > start
   - [ ] Limit range to available data dates
   - [ ] Update Zustand store on change

2. **Build playback controls**
   - [ ] Create `src/components/timeline/PlaybackControls.tsx`
   - [ ] Add Play/Pause button with icon toggle
   - [ ] Add Stop button (resets to start)
   - [ ] Add speed selector dropdown (1x, 10x, 60x, 100x, 500x, 1000x)
   - [ ] Add current speed indicator
   - [ ] Disable controls when no location selected

3. **Build timeline scrubber**
   - [ ] Create `src/components/timeline/TimelineScrubber.tsx`
   - [ ] Display horizontal progress bar
   - [ ] Show start time, end time, current time
   - [ ] Implement draggable scrubber handle
   - [ ] Show hover timestamp on bar
   - [ ] Add tick marks for hours/days
   - [ ] Update current time on drag

4. **Integrate timeline components**
   - [ ] Update `TimelineControls.tsx` to include all subcomponents
   - [ ] Connect to Zustand store for state
   - [ ] Add keyboard shortcuts (Space=play/pause, ←→=scrub)
   - [ ] Style components consistently

**Acceptance Criteria:**

- Date range picker allows valid range selection
- Playback controls are intuitive and responsive
- Scrubber updates current time smoothly
- All controls update global state correctly

#### Day 3-4: SSE Replay Backend

**Tasks:**

1. **Implement replay event generator**
   - [ ] Create `app/services/replay_service.py`
   - [ ] Implement `generate_replay_events(location, start, end, speed, from_time)`
   - [ ] Query events from lakeflow.all_events ordered by timestamp
   - [ ] Stream events with timing based on speed multiplier
   - [ ] Calculate delays between events: `(event2.ts - event1.ts) / speed`
   - [ ] Use `yield` to create async generator

2. **Create SSE replay endpoint**
   - [ ] Install sse-starlette: `pip install sse-starlette`
   - [ ] Create `app/api/replay.py` router
   - [ ] Implement `GET /api/v1/locations/{location}/replay`
   - [ ] Query parameters: start, end, speed, from_time
   - [ ] Use EventSourceResponse for SSE
   - [ ] Send events with proper SSE format

3. **Implement SSE event types**
   - [ ] Send `order_event` for each order lifecycle event
   - [ ] Send `metrics_update` every 60 simulated seconds
   - [ ] Send `replay_position` every 1 real second
   - [ ] Send `replay_complete` at end of range
   - [ ] Include event data in JSON format

4. **Add replay controls**
   - [ ] Support pausing by client disconnect/reconnect
   - [ ] Support speed changes by starting new stream
   - [ ] Support resume with from_time parameter
   - [ ] Handle client disconnections gracefully

**Acceptance Criteria:**

- SSE endpoint streams events correctly
- Timing is accurate based on speed multiplier
- Can reconnect and resume from position
- No memory leaks with long-running streams

#### Day 5: Frontend SSE Client

**Tasks:**

1. **Create SSE client service**
   - [ ] Create `src/services/sseClient.ts`
   - [ ] Implement EventSource connection to /replay endpoint
   - [ ] Parse SSE messages into typed events
   - [ ] Handle connection errors and reconnection
   - [ ] Clean up connection on component unmount

2. **Create replay hook**
   - [ ] Create `src/hooks/useReplay.ts`
   - [ ] Manage SSE connection lifecycle
   - [ ] Dispatch events to Zustand store
   - [ ] Handle play/pause state
   - [ ] Handle speed changes (reconnect with new speed)
   - [ ] Track replay position

3. **Connect timeline to replay**
   - [ ] Update PlaybackControls to start/stop SSE connection
   - [ ] Update speed selector to trigger reconnect
   - [ ] Update scrubber to show current replay position
   - [ ] Show "Live" indicator when replay is active

4. **Update visualizations for replay**
   - [ ] Update map to process order_event messages
   - [ ] Update kitchen pipeline to process metrics_update messages
   - [ ] Update metrics dashboard with new data
   - [ ] Smoothly transition between states

**Acceptance Criteria:**

- Play button starts SSE stream and events flow
- Pause button stops stream without losing position
- Speed changes restart stream at new speed
- All visualizations update in real-time
- Resume works correctly

### Week 6: Driver Animation & Interactivity

#### Day 1-2: Driver Visualization

**Tasks:**

1. **Implement driver markers**
   - [ ] Create `src/components/map/DriverMarkers.tsx`
   - [ ] Extract driver positions from driver_ping events
   - [ ] Display moving markers for active drivers
   - [ ] Use custom car icon
   - [ ] Show driver ID and order ID on hover

2. **Animate driver movement**
   - [ ] Store previous and current position for each driver
   - [ ] Use Mapbox marker animation API
   - [ ] Animate between positions over 1-2 seconds
   - [ ] Update rotation based on direction of travel
   - [ ] Add ping trail (fading breadcrumb trail)

3. **Show delivery progress**
   - [ ] Update route line color based on progress %
   - [ ] Show progress indicator on route (e.g., marker at progress point)
   - [ ] Update ETA display as driver moves
   - [ ] Fade out completed deliveries after 30 seconds

4. **Optimize animation performance**
   - [ ] Batch marker updates
   - [ ] Use requestAnimationFrame for smooth animation
   - [ ] Limit number of simultaneous animations
   - [ ] Test with 20+ concurrent drivers

**Acceptance Criteria:**

- Drivers appear and move smoothly during replay
- Animation timing matches replay speed
- Trail effect shows driver path
- Performance stays above 30 FPS

#### Day 3-4: Event Feed & Order Details

**Tasks:**

1. **Create event feed component**
   - [ ] Create `src/components/EventFeed.tsx`
   - [ ] Display scrollable list of recent events
   - [ ] Show last 50 events (virtual scrolling)
   - [ ] Format each event with icon, type, timestamp, details
   - [ ] Add relative timestamps ("2 min ago")

2. **Process replay events for feed**
   - [ ] Listen to SSE order_event messages
   - [ ] Add new events to feed list
   - [ ] Maintain chronological order
   - [ ] Remove old events (keep last 50)
   - [ ] Auto-scroll to latest event

3. **Style event types**
   - [ ] Use lucide-react icons for each event type
   - [ ] Color-code events (created=gray, cooking=orange, etc.)
   - [ ] Format event details (order items, timings)
   - [ ] Add hover state

4. **Create order detail modal**
   - [ ] Create `src/components/OrderDetailModal.tsx`
   - [ ] Show complete order lifecycle timeline
   - [ ] Display order items and total
   - [ ] Show map with delivery route
   - [ ] Show timing breakdown by stage
   - [ ] Add close button and click-outside-to-close

5. **Connect interactions**
   - [ ] Click event in feed → open order detail modal
   - [ ] Click marker on map → open order detail modal
   - [ ] Click stage in pipeline → filter feed to that stage
   - [ ] Highlight selected order on map

**Acceptance Criteria:**

- Event feed updates in real-time during replay
- Events are formatted clearly and legibly
- Order detail modal shows complete order info
- All click interactions work correctly

#### Day 5: Polish & Bug Fixes

**Tasks:**

1. **Fix edge cases**
   - [ ] Handle replay at very high speeds (1000x)
   - [ ] Handle empty time ranges (no orders)
   - [ ] Handle location with partial data
   - [ ] Handle SSE connection failures
   - [ ] Add retry logic for failed connections

2. **Improve loading states**
   - [ ] Add skeleton loaders for map, pipeline, metrics
   - [ ] Show progress indicator when loading large time range
   - [ ] Add "buffering" indicator during slow replay
   - [ ] Disable interactions while loading

3. **Add user feedback**
   - [ ] Toast notifications for errors
   - [ ] Confirmation for stopping replay
   - [ ] Success message when replay completes
   - [ ] Help tooltips for complex controls

4. **Performance optimization**
   - [ ] Profile React components with React DevTools
   - [ ] Memoize expensive calculations
   - [ ] Debounce map updates
   - [ ] Throttle chart re-renders
   - [ ] Optimize SSE message processing

**Acceptance Criteria:**

- No critical bugs in core functionality
- Loading states provide good user feedback
- Error handling is graceful
- Performance meets targets (<3s load, 30+ FPS)

### Phase 3 Integration & Testing

**Tasks:**

1. **Full replay testing**
   - [ ] Test 1-hour replay at various speeds
   - [ ] Test pause/resume functionality
   - [ ] Test scrubbing to different times
   - [ ] Test location switching during replay
   - [ ] Verify data accuracy at different timestamps

2. **Stress testing**
   - [ ] Test with 100+ orders in time range
   - [ ] Test replay at 1000x speed
   - [ ] Monitor memory usage over long replays
   - [ ] Check for memory leaks
   - [ ] Test with poor network conditions

3. **Cross-browser testing**
   - [ ] Test in Chrome, Firefox, Safari
   - [ ] Verify SSE works in all browsers
   - [ ] Check map rendering differences
   - [ ] Test animations across browsers

**Phase 3 Deliverables:**

- ✅ Full replay functionality with timeline controls
- ✅ SSE streaming with play/pause/speed controls
- ✅ Animated driver visualization
- ✅ Event feed showing recent activity
- ✅ Order detail modal with complete lifecycle
- ✅ All interactions working correctly

**Phase 3 Exit Criteria:**

- Replay works smoothly at all speeds
- No critical performance issues
- All interactions are intuitive
- Ready for demo polish

---

## Phase 4: Polish & Demo Prep (Week 7)

**Goal:** Final polish, documentation, demo preparation, and deployment

**Duration:** 1 week (40 hours)

**Deliverables:**

- Production-ready application
- Complete documentation
- Demo script and talking points
- Deployment to Databricks Apps
- Demo video recording

### Day 1-2: Visual Polish & UX

**Tasks:**

1. **Design refinements**
   - [ ] Review entire UI for consistency
   - [ ] Update color scheme for better contrast
   - [ ] Improve spacing and alignment
   - [ ] Add subtle animations (fade-ins, transitions)
   - [ ] Polish icons and button states

2. **Responsive design**
   - [ ] Test on different screen sizes (1920x1080, 1366x768)
   - [ ] Adjust layout breakpoints
   - [ ] Ensure text is readable at all sizes
   - [ ] Test map interactions on different sizes

3. **Empty states**
   - [ ] Add empty state for no location selected
   - [ ] Add empty state for no orders in time range
   - [ ] Add empty state for event feed
   - [ ] Style empty states attractively

4. **Error states**
   - [ ] Add error boundary component
   - [ ] Style error messages consistently
   - [ ] Add retry buttons for recoverable errors
   - [ ] Log errors for debugging

5. **Loading states**
   - [ ] Ensure all async operations show loading
   - [ ] Use skeleton loaders instead of spinners where appropriate
   - [ ] Show progress for long operations
   - [ ] Add loading overlays for blocking operations

**Acceptance Criteria:**

- UI looks polished and professional
- No visual glitches or inconsistencies
- Empty and error states are helpful
- Loading states provide clear feedback

### Day 3: Documentation

**Tasks:**

1. **User documentation**
   - [ ] Create `apps/digital-twin/README.md`
   - [ ] Document how to use the application
   - [ ] Explain each feature (timeline, map, pipeline, metrics)
   - [ ] Add screenshots of key features
   - [ ] Include troubleshooting section

2. **Developer documentation**
   - [ ] Document project structure
   - [ ] Explain architecture decisions
   - [ ] Document API endpoints with examples
   - [ ] Add JSDoc comments to complex functions
   - [ ] Document environment variables

3. **Deployment guide**
   - [ ] Document Databricks Apps deployment process
   - [ ] List prerequisites and dependencies
   - [ ] Provide step-by-step deployment instructions
   - [ ] Document configuration options
   - [ ] Add rollback procedures

4. **Update CLAUDE.md**
   - [ ] Add digital twin section to main CLAUDE.md
   - [ ] Document development workflow
   - [ ] Link to detailed specification
   - [ ] Add common issues and solutions

**Acceptance Criteria:**

- Documentation is clear and comprehensive
- New developers can set up project from docs
- Users can understand how to use the app
- Deployment process is well-documented

### Day 4: Deployment & Testing

**Tasks:**

1. **Create deployment notebook**
   - [ ] Create `stages/digital_twin.ipynb`
   - [ ] Import uc_state utilities
   - [ ] Get CATALOG parameter from widgets
   - [ ] Deploy app using Databricks SDK
   - [ ] Track app in UC state
   - [ ] Add error handling

2. **Create app.yaml configuration**
   - [ ] Define app name and description
   - [ ] Configure uvicorn command
   - [ ] Set environment variables (CATALOG, schemas)
   - [ ] Configure resources (min/max replicas)
   - [ ] Set health check endpoints

3. **Build and deploy**
   - [ ] Build frontend: `npm run build`
   - [ ] Verify static files in app/static/
   - [ ] Test locally with production build
   - [ ] Deploy to Databricks Apps
   - [ ] Verify app URL is accessible

4. **Integration with Casper's job**
   - [ ] Update `databricks.yml`
   - [ ] Add Digital_Twin_App task
   - [ ] Set dependency on Spark_Declarative_Pipeline
   - [ ] Test bundle deploy: `databricks bundle deploy`
   - [ ] Run digital twin task from job

5. **Production testing**
   - [ ] Test deployed app with real data
   - [ ] Verify all features work in production
   - [ ] Check performance and latency
   - [ ] Monitor logs for errors
   - [ ] Test with multiple locations

**Acceptance Criteria:**

- App deploys successfully via Databricks bundle
- All features work in production environment
- Performance meets targets
- No critical errors in logs
- App is accessible at Databricks URL

### Day 5: Demo Prep & Finalization

**Tasks:**

1. **Create demo script**
   - [ ] Write talking points for each feature
   - [ ] Plan demo flow (5-10 minute presentation)
   - [ ] Identify impressive moments to highlight
   - [ ] Prepare answers to expected questions
   - [ ] Create backup plan for technical issues

2. **Demo flow structure**
   ```
   1. Introduction (30s)
      - Explain ghost kitchen context
      - Show Casper's data flow diagram
   
   2. Location Overview (1 min)
      - Select San Francisco location
      - Highlight order volume and date range
      - Show map overview of delivery area
   
   3. Kitchen Operations (2 min)
      - Explain pipeline stages
      - Start replay at 60x speed
      - Watch orders flow through kitchen
      - Point out peak hours
   
   4. Delivery Tracking (2 min)
      - Show drivers appearing on map
      - Follow one delivery from start to finish
      - Highlight GPS tracking animation
      - Show route optimization
   
   5. Business Metrics (1 min)
      - Show KPI dashboard
      - Explain key metrics (delivery time, throughput)
      - Show trend charts
   
   6. Interactive Features (2 min)
      - Click order for details
      - Scrub timeline to interesting moment
      - Switch locations (SF → Chicago)
      - Show event feed
   
   7. Conclusion (1 min)
      - Summarize capabilities
      - Mention future enhancements
      - Open for questions
   ```

3. **Record demo video**
   - [ ] Set up screen recording software
   - [ ] Practice demo flow 2-3 times
   - [ ] Record full demo walkthrough
   - [ ] Add voiceover explaining features
   - [ ] Edit video for clarity
   - [ ] Export and share with team

4. **Create demo environment**
   - [ ] Identify best time range for demo (active period)
   - [ ] Verify data quality for demo location
   - [ ] Create bookmarks for interesting moments
   - [ ] Set default view to showcase key features
   - [ ] Test demo flow 3+ times

5. **Prepare supporting materials**
   - [ ] Create 1-page feature summary
   - [ ] Export screenshots of key screens
   - [ ] Prepare architecture diagram
   - [ ] Create FAQ document
   - [ ] Prepare handoff instructions for ops team

**Acceptance Criteria:**

- Demo script is clear and engaging
- Demo video shows all key features
- Demo environment is stable and impressive
- Supporting materials are professional
- Ready to present to stakeholders

### Final Checklist

**Code Quality:**

- [ ] All linting errors fixed (ESLint, Pylint)
- [ ] All TypeScript errors resolved
- [ ] No console.log or debug statements in production
- [ ] All tests passing (>80% coverage target)
- [ ] Code reviewed by peer (if available)

**Performance:**

- [ ] Page load time <3 seconds
- [ ] API response times <2 seconds
- [ ] Replay runs smoothly at 60x speed
- [ ] Map animations maintain 30+ FPS
- [ ] No memory leaks during extended use

**Functionality:**

- [ ] All features work as specified
- [ ] Error handling is comprehensive
- [ ] Edge cases are handled
- [ ] Data accuracy verified against source tables
- [ ] All interactions are intuitive

**Documentation:**

- [ ] README is complete and accurate
- [ ] API documentation is up-to-date
- [ ] Deployment guide is tested
- [ ] User guide includes screenshots
- [ ] CLAUDE.md is updated

**Deployment:**

- [ ] App deploys via databricks bundle
- [ ] App is tracked in UC state
- [ ] App URL is accessible
- [ ] Environment variables are configured
- [ ] Logs are being captured

**Demo:**

- [ ] Demo script finalized
- [ ] Demo video recorded
- [ ] Demo environment prepared
- [ ] Supporting materials ready
- [ ] Team trained on demo flow

**Phase 4 Deliverables:**

- ✅ Production-ready application deployed
- ✅ Complete documentation suite
- ✅ Demo script and video
- ✅ All code quality checks passed
- ✅ App integrated into Casper's platform

**Phase 4 Exit Criteria:**

- Application is production-ready
- Demo is polished and impressive
- Documentation is comprehensive
- Team is prepared to present
- **PROJECT COMPLETE** 🎉

---

## Post-Launch Activities

### Week 8+: Maintenance & Iteration

**Monitoring:**

- [ ] Set up error tracking (if available)
- [ ] Monitor usage patterns
- [ ] Track performance metrics
- [ ] Collect user feedback

**Iteration:**

- [ ] Prioritize bug fixes based on severity
- [ ] Gather enhancement requests
- [ ] Plan Phase 2 features (multi-location, 3D, real-time)
- [ ] Update roadmap based on feedback

**Knowledge Transfer:**

- [ ] Conduct walkthrough with operations team
- [ ] Answer questions from stakeholders
- [ ] Share lessons learned
- [ ] Document known issues and workarounds

---

## Risk Management

### High-Risk Items

| Risk | Mitigation | Owner |
|------|------------|-------|
| **SSE connection instability** | Implement reconnection logic, fallback to polling | Backend Dev |
| **Map performance with many markers** | Implement clustering, virtualization | Frontend Dev |
| **Slow database queries** | Add indexes, optimize SQL, implement caching | Backend Dev |
| **Deployment issues** | Test early, document thoroughly, have rollback plan | DevOps |
| **Data quality problems** | Validate data, add error handling, test with edge cases | Both |

### Medium-Risk Items

| Risk | Mitigation | Owner |
|------|------------|-------|
| **Scope creep** | Stick to phased plan, defer Phase 2 features | PM |
| **Timeline slippage** | Track progress daily, adjust scope if needed | PM |
| **Integration issues** | Test integration early and often | Both |
| **Browser compatibility** | Test in all major browsers regularly | Frontend Dev |

### Low-Risk Items

| Risk | Mitigation | Owner |
|------|------------|-------|
| **Design changes** | Lock design in Phase 1, defer polish to Phase 4 | Designer |
| **Learning curve (new tech)** | Allow time for research, pair programming | Both |
| **Demo environment issues** | Have backup demo data, test repeatedly | PM |

---

## Success Metrics

### Development Metrics

- **Velocity:** Complete all phases on schedule (±3 days acceptable)
- **Quality:** >80% test coverage, <5 critical bugs at launch
- **Performance:** Page load <3s, replay smooth at 60x, API <2s
- **Documentation:** All sections complete, peer-reviewed

### Demo Metrics

- **Engagement:** Audience actively asks questions and explores features
- **Comprehension:** >90% of viewers understand kitchen operations flow
- **Impact:** Positive feedback from 3+ stakeholders
- **Conversion:** Used in 5+ customer demos within 1 month

### Technical Metrics

- **Uptime:** >99% availability (for demo purposes)
- **Errors:** <1% of API requests fail
- **Performance:** Consistent FPS during replay, no memory leaks
- **Scalability:** Ready to expand to real-time mode in Phase 2

---

## Resource Requirements

### Development Team

- **1 Backend Developer:** Python, FastAPI, SQL expertise
- **1 Frontend Developer:** React, TypeScript, Mapbox expertise
- **OR 1 Full-Stack Developer:** Can handle both (adds 1-2 weeks)

### Infrastructure

- **Databricks Workspace:** With access to Casper's lakeflow tables
- **SQL Warehouse:** For querying lakeflow tables (Small size sufficient)
- **Databricks Apps:** Hosting for deployed application
- **Development Environment:** Local machines with Docker/Node.js/Python

### Tools & Services

- **Mapbox API:** Free tier sufficient for demo (50k map loads/month)
- **Version Control:** Git repository (GitHub/GitLab)
- **Code Editor:** VS Code recommended
- **Testing Tools:** Jest, Pytest, Playwright (optional)
- **Screen Recording:** For demo video (Loom, OBS, or built-in)

### Budget Estimate

- **Development Time:** 7 weeks × 40 hours × $100/hour = $28,000
- **Databricks Compute:** ~$100/month for SQL warehouse and app hosting
- **Mapbox API:** $0 (free tier)
- **Tools/Licenses:** ~$100/month (optional)
- **Total:** ~$28,500 for complete project

---

## Appendix: Task Estimation Details

### Phase 1 Breakdown (80 hours)

- Backend setup: 16 hours
- Database connectivity: 12 hours
- API endpoints: 12 hours
- React setup: 12 hours
- State management: 8 hours
- UI components: 16 hours
- Testing & integration: 4 hours

### Phase 2 Breakdown (80 hours)

- Mapbox integration: 16 hours
- Backend order endpoints: 12 hours
- Map visualization: 16 hours
- Kitchen status backend: 8 hours
- Kitchen pipeline UI: 12 hours
- Metrics dashboard: 12 hours
- Testing & integration: 4 hours

### Phase 3 Breakdown (80 hours)

- Timeline UI: 12 hours
- SSE backend: 16 hours
- SSE frontend: 12 hours
- Driver animation: 16 hours
- Event feed & modal: 12 hours
- Polish & bug fixes: 8 hours
- Testing & integration: 4 hours

### Phase 4 Breakdown (40 hours)

- Visual polish: 8 hours
- Documentation: 12 hours
- Deployment: 8 hours
- Demo prep: 8 hours
- Final testing: 4 hours

**Total: 280 hours (7 weeks)**

---

**Plan Status:** READY FOR EXECUTION  
**Next Steps:** Assign resources → Begin Phase 1 → Track progress daily

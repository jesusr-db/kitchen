# Casper's Kitchens Digital Twin Frontend

Real-time visualization and historical replay of ghost kitchen operations.

## Overview

This application provides an interactive digital twin interface for visualizing Casper's Kitchens operations, including:

- **Delivery Map**: Real-time driver tracking and route visualization
- **Kitchen Pipeline**: Order flow through cooking stages
- **Metrics Dashboard**: KPIs and performance analytics
- **Historical Replay**: Time travel through order history with playback controls

## Architecture

- **Backend**: FastAPI (Python) connecting to Databricks lakeflow tables
- **Frontend**: React + TypeScript + Tailwind CSS + React Leaflet
- **Deployment**: Databricks Apps framework
- **Data Source**: Casper's Kitchens lakeflow tables (gold_*, silver_*)
- **Maps**: React Leaflet with OpenStreetMap tiles (no API key required)

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- Access to Databricks workspace with Casper's data

### Backend Setup

1. Install dependencies:
   ```bash
   cd apps/digital-twin
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your Databricks connection details
   ```

3. Run backend:
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will be available at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run development server:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

3. Build for production:
   ```bash
   npm run build
   ```

   Output will be in `../app/static/`

## Deployment

### Via Databricks Bundle

```bash
# From repository root
databricks bundle deploy
databricks bundle run caspers
```

The digital twin app will be deployed as part of the `Digital_Twin_App` task.

### Manual Deployment

Run the `stages/digital_twin.ipynb` notebook in your Databricks workspace.

## API Endpoints

### `GET /api/v1/locations`

Get list of available ghost kitchen locations.

**Response:**
```json
{
  "locations": [
    {
      "location_name": "sanfrancisco",
      "display_name": "San Francisco",
      "gk_lat": 37.7749,
      "gk_lon": -122.4194,
      "radius_mi": 4.0,
      "total_orders": 15234,
      "date_range": {
        "start": "2025-10-14T00:00:00Z",
        "end": "2025-10-17T23:59:59Z"
      }
    }
  ]
}
```

## Project Structure

```
apps/digital-twin/
├── app/                    # Backend (FastAPI)
│   ├── api/               # API endpoints
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   ├── config.py          # Configuration
│   ├── db.py              # Database connectivity
│   └── main.py            # FastAPI app
├── frontend/              # Frontend (React)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API client
│   │   ├── store/         # State management (Zustand)
│   │   └── types/         # TypeScript types
│   └── package.json
├── tests/                 # Backend tests
├── app.yaml              # Databricks Apps config
├── requirements.txt      # Python dependencies
└── README.md
```

## Current Status: Phase 1 Complete

✅ **Backend Foundation**
- FastAPI server with database connectivity
- Location management API
- Data models and service layer
- Health check endpoint

✅ **Frontend Foundation**
- React + TypeScript setup
- Tailwind CSS styling
- Location selector component
- App layout and routing
- State management (Zustand)
- API client (TanStack Query)

🚧 **Coming in Phase 2** (Weeks 3-4)
- Map visualization with React Leaflet
- Kitchen pipeline UI
- Metrics dashboard
- Time range queries

🚧 **Coming in Phase 3** (Weeks 5-6)
- Historical replay with SSE
- Timeline controls
- Driver animation
- Event feed

## Development Roadmap

See `claudedocs/digital-twin-implementation-plan.md` for detailed phased implementation plan.

## Troubleshooting

### Backend Issues

**Connection error to Databricks:**
- Verify `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, and `DATABRICKS_TOKEN` in environment
- Check SQL warehouse is running
- Verify network connectivity

**No locations returned:**
- Verify lakeflow tables exist: `{CATALOG}.lakeflow.all_events`
- Check data generator has created events
- Run raw_data and lakeflow stages first

### Frontend Issues

**API calls failing:**
- Verify backend is running on `http://localhost:8000`
- Check Vite proxy configuration in `vite.config.ts`
- Open browser DevTools Network tab for details

**Build errors:**
- Run `npm install` to ensure dependencies are installed
- Check Node.js version (18+ required)
- Clear node_modules and reinstall if needed

## License

Part of Casper's Kitchens demo platform.
© 2025 Databricks, Inc.

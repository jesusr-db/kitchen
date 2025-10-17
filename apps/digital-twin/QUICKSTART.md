# Digital Twin Quick Start Guide

## 🚀 Phase 1 Setup (5 Minutes)

### Step 1: Verify Project Structure

```bash
cd apps/digital-twin
tree -L 2 -I "node_modules|__pycache__|.git"
```

You should see:
```
apps/digital-twin/
├── app/                # Backend
├── frontend/           # Frontend
├── tests/             # Tests
├── app.yaml           # Deployment config
├── requirements.txt   # Python deps
└── README.md
```

### Step 2: Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (for local dev only)
export CATALOG=caspers
export SIMULATOR_SCHEMA=simulator
export LAKEFLOW_SCHEMA=lakeflow

# If running locally (not in Databricks), also set:
# export DATABRICKS_HOST=your-workspace.databricks.com
# export DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
# export DATABRICKS_TOKEN=your-token

# Start backend
uvicorn app.main:app --reload
```

**Verify backend is running:**
- Open `http://localhost:8000/health`
- Should return: `{"status": "healthy", "app": "caspers-digital-twin", ...}`
- Check API docs: `http://localhost:8000/docs`

### Step 3: Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

**Verify frontend is running:**
- Open `http://localhost:5173`
- Should see "Casper's Kitchens Digital Twin" header
- Location selector dropdown should load locations from API

### Step 4: Test End-to-End

1. Backend running on `:8000` ✓
2. Frontend running on `:5173` ✓
3. Select a location from dropdown
4. Main view should show placeholder panels for map, pipeline, and metrics

**Success!** Phase 1 foundation is complete.

## 🔍 Troubleshooting

### Backend won't start

**Error: `databricks-sql-connector` import fails**
```bash
pip install --upgrade databricks-sql-connector
```

**Error: Connection to Databricks fails**
- Check environment variables are set correctly
- Verify SQL warehouse is running in Databricks
- Test connection with `databricks-sql-cli` if available

### Frontend won't start

**Error: `npm install` fails**
```bash
# Clear cache and try again
rm -rf node_modules package-lock.json
npm install
```

**Error: TypeScript errors**
- Ensure Node.js version is 18+ (`node --version`)
- Try: `npm run build` to see specific errors

### API calls failing (404 or CORS errors)

**Check Vite proxy:**
- Verify backend is running on port 8000
- Check `vite.config.ts` proxy configuration
- Open browser DevTools → Network tab to see actual requests

**CORS errors:**
- Backend should allow all origins in development
- Check `app/main.py` CORS middleware configuration

## 📋 Phase 1 Checklist

- [x] Backend server starts successfully
- [x] `/health` endpoint responds
- [x] `/api/v1/locations` returns location data
- [x] Frontend dev server starts
- [x] Location selector loads and displays locations
- [x] Can select a location and see main view
- [x] No console errors in browser DevTools

## 🎯 Next Steps

**Phase 2** (Weeks 3-4):
- Implement Mapbox map visualization
- Add customer markers and route lines
- Build kitchen pipeline UI
- Create metrics dashboard with KPIs

See `claudedocs/digital-twin-implementation-plan.md` for complete roadmap.

## 🆘 Getting Help

1. Check `README.md` for detailed documentation
2. Review implementation plan: `claudedocs/digital-twin-implementation-plan.md`
3. Review spec: `claudedocs/digital-twin-spec.md`
4. Check backend logs: Terminal where `uvicorn` is running
5. Check frontend errors: Browser DevTools Console

## 🎉 Demo Phase 1

To show what's working:

1. **Start both servers** (backend + frontend)
2. **Open app** → `http://localhost:5173`
3. **Show location selector** → Dropdown loads real data from Casper's tables
4. **Select SF or Chicago** → Main view updates with location name
5. **Show API** → `http://localhost:8000/docs` for interactive API docs

**Key Achievement:** Full stack running with real Databricks data integration!

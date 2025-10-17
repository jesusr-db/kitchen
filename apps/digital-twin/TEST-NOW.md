# 🚀 Test Digital Twin - Quick Start

## ✅ Pre-Test Validation

All Phase 1 files created successfully:
- ✓ 14 Python backend files
- ✓ 13 TypeScript frontend files  
- ✓ All syntax valid
- ✓ All config files present

## 📋 Quick Test (5 Minutes)

### Terminal 1: Backend

```bash
cd /Users/jesus.rodriguez/Documents/gitRepos/caspers-kitchens/apps/digital-twin

# Install dependencies (first time only)
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

**Wait for:**
```
INFO:     Application startup complete.
```

**Test:** Open http://localhost:8000/health
**Should see:** `{"status": "healthy", ...}`

### Terminal 2: Frontend

```bash
cd /Users/jesus.rodriguez/Documents/gitRepos/caspers-kitchens/apps/digital-twin/frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

**Wait for:**
```
➜  Local:   http://localhost:5173/
```

**Test:** Open http://localhost:5173
**Should see:** Casper's Kitchens Digital Twin with location dropdown

## ✅ Success Criteria

1. **Backend running** on port 8000 ✓
2. **Frontend running** on port 5173 ✓
3. **Location selector** loads and displays locations ✓
4. **Can select location** and main view updates ✓
5. **No errors** in browser console ✓

## 🎯 What You'll See

```
┌─────────────────────────────────────────────────────────┐
│ 🍴 Casper's Kitchens         [San Francisco ▼]        │
│    Digital Twin Operations Monitor                     │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────────┬─────────────────────────┐   │
│ │                        │  Kitchen Pipeline       │   │
│ │   Delivery Map         │  [Coming in Phase 2]    │   │
│ │   [Coming in Phase 2]  ├─────────────────────────┤   │
│ │                        │  Metrics                │   │
│ │                        │  [Coming in Phase 2]    │   │
│ └────────────────────────┴─────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🐛 Common Issues

**Backend won't start:**
- Run: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (need 3.10+)

**Frontend won't start:**
- Run: `npm install`
- Check Node version: `node --version` (need 18+)

**API calls failing:**
- Make sure backend is running on port 8000
- Check http://localhost:8000/health works

## 📚 Full Documentation

- **Setup Guide**: `QUICKSTART.md`
- **Project Docs**: `README.md`
- **Test Results**: `../../../claudedocs/digital-twin-test-results.md`
- **Implementation Plan**: `../../../claudedocs/digital-twin-implementation-plan.md`

## 🎉 Phase 1 Complete!

Once both servers are running and you can select a location, **Phase 1 is validated**. Ready for Phase 2!

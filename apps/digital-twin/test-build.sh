#!/bin/bash
set -e

echo "🧪 Casper's Digital Twin - Phase 1 Build Test"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

test_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "1️⃣ Environment Checks"
echo "--------------------"

# Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
if [[ "$PYTHON_VERSION" =~ ^3\.(10|11|12|13) ]]; then
    test_pass "Python version: $PYTHON_VERSION"
else
    test_fail "Python version: $PYTHON_VERSION (need 3.10+)"
fi

# Node version
NODE_VERSION=$(node --version | sed 's/v//')
NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
if [ "$NODE_MAJOR" -ge 18 ]; then
    test_pass "Node version: v$NODE_VERSION"
else
    test_fail "Node version: v$NODE_VERSION (need 18+)"
fi

# npm version
NPM_VERSION=$(npm --version)
test_pass "npm version: $NPM_VERSION"

echo ""
echo "2️⃣ Project Structure"
echo "--------------------"

# Check directories
for dir in app frontend tests; do
    if [ -d "$dir" ]; then
        test_pass "Directory exists: $dir/"
    else
        test_fail "Missing directory: $dir/"
    fi
done

# Check key files
for file in requirements.txt app.yaml README.md; do
    if [ -f "$file" ]; then
        test_pass "File exists: $file"
    else
        test_fail "Missing file: $file"
    fi
done

echo ""
echo "3️⃣ Backend Files"
echo "----------------"

# Check backend structure
BACKEND_FILES=(
    "app/__init__.py"
    "app/main.py"
    "app/config.py"
    "app/db.py"
    "app/api/locations.py"
    "app/models/location.py"
    "app/services/location_service.py"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_pass "$file"
    else
        test_fail "Missing: $file"
    fi
done

echo ""
echo "4️⃣ Frontend Files"
echo "-----------------"

FRONTEND_FILES=(
    "frontend/package.json"
    "frontend/vite.config.ts"
    "frontend/tsconfig.json"
    "frontend/index.html"
    "frontend/src/main.tsx"
    "frontend/src/App.tsx"
    "frontend/src/store/appStore.ts"
    "frontend/src/services/api.ts"
)

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_pass "$file"
    else
        test_fail "Missing: $file"
    fi
done

echo ""
echo "5️⃣ Python Syntax Check"
echo "----------------------"

# Check Python files for syntax errors
PYTHON_ERRORS=0
for pyfile in $(find app -name "*.py" 2>/dev/null); do
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        test_pass "Syntax valid: $pyfile"
    else
        test_fail "Syntax error: $pyfile"
        ((PYTHON_ERRORS++))
    fi
done

if [ $PYTHON_ERRORS -eq 0 ]; then
    test_pass "All Python files have valid syntax"
fi

echo ""
echo "6️⃣ TypeScript Configuration"
echo "---------------------------"

cd frontend

# Check package.json
if [ -f "package.json" ]; then
    test_pass "package.json found"
    
    # Check for required dependencies
    if grep -q "react" package.json; then
        test_pass "React dependency declared"
    else
        test_fail "React dependency missing"
    fi
    
    if grep -q "typescript" package.json; then
        test_pass "TypeScript dependency declared"
    else
        test_fail "TypeScript dependency missing"
    fi
else
    test_fail "package.json not found"
fi

cd ..

echo ""
echo "7️⃣ Configuration Files"
echo "----------------------"

# Check .env.example
if [ -f ".env.example" ]; then
    test_pass ".env.example exists"
    if grep -q "CATALOG" .env.example; then
        test_pass "CATALOG variable documented"
    fi
fi

# Check app.yaml
if [ -f "app.yaml" ]; then
    test_pass "app.yaml exists"
    if grep -q "caspers-digital-twin" app.yaml; then
        test_pass "App name configured"
    fi
fi

echo ""
echo "8️⃣ Documentation"
echo "----------------"

if [ -f "README.md" ]; then
    LINES=$(wc -l < README.md)
    test_pass "README.md exists ($LINES lines)"
fi

if [ -f "QUICKSTART.md" ]; then
    test_pass "QUICKSTART.md exists"
fi

echo ""
echo "📊 Test Summary"
echo "==============="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
fi
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Install backend dependencies: pip install -r requirements.txt"
    echo "2. Install frontend dependencies: cd frontend && npm install"
    echo "3. Start backend: uvicorn app.main:app --reload"
    echo "4. Start frontend: cd frontend && npm run dev"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo "Please check the errors above"
    exit 1
fi

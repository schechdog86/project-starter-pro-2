#!/usr/bin/env bash
set -euo pipefail

# Test API endpoints for orchestrator system

BASE_URL="http://127.0.0.1:8000"

echo "🧪 Testing Orchestrator API Endpoints"
echo "======================================"
echo ""

# Check if backend is running
echo "1️⃣  Checking if backend is running..."
if ! curl -s "${BASE_URL}/api/skills" > /dev/null 2>&1; then
    echo "❌ Backend not running. Please start it first:"
    echo "   cd backend && uvicorn main:app --reload"
    exit 1
fi
echo "✅ Backend is running"
echo ""

# List skills
echo "2️⃣  Listing all skills..."
curl -s "${BASE_URL}/api/skills" | python3 -m json.tool
echo ""

# Get web_search skill info
echo "3️⃣  Getting web_search skill info..."
curl -s "${BASE_URL}/api/skills/web_search" | python3 -m json.tool
echo ""

# Approve web_search skill
echo "4️⃣  Approving web_search skill..."
curl -s -X POST "${BASE_URL}/api/skills/web_search/approve" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' | python3 -m json.tool
echo ""

# Execute web_search skill
echo "5️⃣  Executing web_search skill..."
curl -s -X POST "${BASE_URL}/api/skills/web_search/execute" \
  -H "Content-Type: application/json" \
  -d '{"params": {"query": "AI frameworks 2025", "num_results": 3}}' | python3 -m json.tool
echo ""

# Get orchestrator status
echo "6️⃣  Getting orchestrator status..."
curl -s "${BASE_URL}/ai/orchestrator/status" | python3 -m json.tool
echo ""

# Execute memory_search skill
echo "7️⃣  Executing memory_search skill..."
curl -s -X POST "${BASE_URL}/api/skills/memory_search/execute" \
  -H "Content-Type: application/json" \
  -d '{"params": {"query": "test", "k": 5}}' | python3 -m json.tool
echo ""

# Get audit log
echo "8️⃣  Getting audit log..."
curl -s "${BASE_URL}/ai/orchestrator/audit-log?limit=5" | python3 -m json.tool
echo ""

echo "✅ All API tests completed!"


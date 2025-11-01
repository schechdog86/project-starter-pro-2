#!/usr/bin/env python3
"""
Quick Test Script
-----------------
Test orchestrator components without starting the full backend.
"""

import sys
import os

# Set test environment variables BEFORE importing anything
os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key-for-testing"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-dummy-key"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-dummy-key"
os.environ["SECRET_KEY"] = "test-secret-key-for-development-only"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🧪 Testing Orchestrator Components")
print("=" * 60)
print()

# Test 1: Import orchestrator
print("1️⃣  Testing orchestrator import...")
try:
    from backend.app.ai.orchestrator import orchestrator
    print("✅ Orchestrator imported successfully")
except Exception as e:
    print(f"❌ Failed to import orchestrator: {e}")
    sys.exit(1)
print()

# Test 2: List skills
print("2️⃣  Testing skill registry...")
try:
    skills = orchestrator.list_skills()
    print(f"✅ Found {len(skills)} skills:")
    for skill in skills:
        print(f"   - {skill}")
except Exception as e:
    print(f"❌ Failed to list skills: {e}")
print()

# Test 3: Get skill info
print("3️⃣  Testing get skill info...")
try:
    info = orchestrator.get_skill_info("web_search")
    if info:
        print(f"✅ web_search skill info:")
        print(f"   Name: {info.get('name')}")
        print(f"   Version: {info.get('version')}")
        print(f"   Enabled: {info.get('enabled')}")
        print(f"   Description: {info.get('description')}")
    else:
        print("❌ web_search skill not found")
except Exception as e:
    print(f"❌ Failed to get skill info: {e}")
print()

# Test 4: Approve skill
print("4️⃣  Testing skill approval...")
try:
    success = orchestrator.approve_skill("web_search", enabled=True)
    if success:
        print("✅ web_search skill approved and enabled")
        info = orchestrator.get_skill_info("web_search")
        print(f"   Enabled status: {info.get('enabled')}")
    else:
        print("❌ Failed to approve skill")
except Exception as e:
    print(f"❌ Failed to approve skill: {e}")
print()

# Test 5: Load skill
print("5️⃣  Testing skill loading...")
try:
    skill = orchestrator.load_skill("web_search")
    if skill:
        print(f"✅ web_search skill loaded: {type(skill).__name__}")
    else:
        print("❌ Failed to load skill")
except Exception as e:
    print(f"❌ Failed to load skill: {e}")
print()

# Test 6: Execute skill (if enabled)
print("6️⃣  Testing skill execution...")
try:
    result = orchestrator.execute_skill("web_search", {
        "query": "AI frameworks 2025",
        "num_results": 3
    })
    print(f"✅ Skill executed successfully")
    print(f"   Result type: {type(result)}")
    if isinstance(result, dict) and "results" in result:
        print(f"   Found {len(result['results'])} results:")
        for i, r in enumerate(result['results'][:3], 1):
            print(f"   {i}. {r[:60]}...")
except Exception as e:
    print(f"⚠️  Skill execution failed (may need network): {e}")
print()

# Test 7: Memory search skill
print("7️⃣  Testing memory search skill...")
try:
    # Insert test data
    orchestrator.memory.insert("Test data about Python programming", title="Test")
    
    # Search
    result = orchestrator.execute_skill("memory_search", {
        "query": "Python",
        "k": 5
    })
    print(f"✅ Memory search executed")
    print(f"   Found {len(result)} memories")
except Exception as e:
    print(f"⚠️  Memory search failed: {e}")
print()

# Test 8: Orchestrator status
print("8️⃣  Testing orchestrator status...")
try:
    status = orchestrator.get_status()
    print("✅ Orchestrator status:")
    print(f"   Agents: {status.get('agents')}")
    print(f"   Skills: {status.get('skills')}")
    print(f"   Audit log size: {status.get('audit_log_size')}")
    print(f"   Available skills: {', '.join(status.get('available_skills', []))}")
except Exception as e:
    print(f"❌ Failed to get status: {e}")
print()

# Test 9: Audit log
print("9️⃣  Testing audit log...")
try:
    log = orchestrator.get_audit_log(limit=5)
    print(f"✅ Retrieved {len(log)} audit log entries")
    if log:
        print("   Recent events:")
        for entry in log[-3:]:
            print(f"   - {entry.get('event')}: {entry.get('data')}")
except Exception as e:
    print(f"❌ Failed to get audit log: {e}")
print()

# Test 10: Create agent
print("🔟 Testing agent creation...")
try:
    success = orchestrator.create_agent(
        "test_agent",
        {"role": "Tester", "policy": "auto"},
        approve=True
    )
    if success:
        print("✅ Agent created successfully")
        agents = orchestrator.list_agents()
        print(f"   Loaded agents: {', '.join(agents)}")
    else:
        print("⚠️  Agent creation pending approval")
except Exception as e:
    print(f"❌ Failed to create agent: {e}")
print()

print("=" * 60)
print("🎉 Component tests completed!")
print()
print("To test the full API:")
print("1. Install dependencies: pip install -r backend/requirements.txt")
print("2. Start backend: cd backend && uvicorn main:app --reload")
print("3. Run API tests: ./scripts/test_api.sh")


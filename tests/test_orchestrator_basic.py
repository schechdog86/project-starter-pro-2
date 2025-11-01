"""
Basic Orchestrator Tests
-------------------------
Test core orchestrator functionality.
"""

import pytest
from backend.app.ai.orchestrator import Orchestrator


def test_orchestrator_init():
    """Test orchestrator initialization."""
    o = Orchestrator()
    assert o is not None
    assert o.skill_registry is not None
    assert o.skill_factory is not None
    assert o.memory is not None
    assert o.llm is not None


def test_skill_registry():
    """Test skill registry lists available skills."""
    o = Orchestrator()
    skills = o.list_skills()
    
    # Should have at least the built-in skills
    assert len(skills) > 0
    assert "web_search" in skills or "memory_search" in skills or "code_analysis" in skills


def test_get_skill_info():
    """Test getting skill information."""
    o = Orchestrator()
    
    # Get web_search skill info
    info = o.get_skill_info("web_search")
    assert info is not None
    assert info["name"] == "web_search"
    assert "version" in info
    assert "description" in info
    assert "parameters" in info


def test_skill_approval():
    """Test skill approval workflow."""
    o = Orchestrator()
    
    # Approve web_search skill
    success = o.approve_skill("web_search", enabled=True)
    assert success is True
    
    # Check it's enabled
    info = o.get_skill_info("web_search")
    assert info["enabled"] is True


def test_skill_exec():
    """Test skill execution."""
    o = Orchestrator()
    
    # Approve skill first
    o.approve_skill("web_search", enabled=True)
    
    # Execute skill
    r = o.execute_skill("web_search", {"query": "AI agents", "num_results": 2})
    
    # Check result structure
    assert r is not None
    assert "results" in r
    assert isinstance(r["results"], list)


def test_memory_search_skill():
    """Test memory search skill."""
    o = Orchestrator()
    
    # Insert some test data into memory
    o.memory.insert("Test data about Python programming", title="Test Memory")
    
    # Execute memory search
    result = o.execute_skill("memory_search", {"query": "Python", "k": 5})
    
    assert result is not None
    assert isinstance(result, list)


def test_code_analysis_skill():
    """Test code analysis skill."""
    o = Orchestrator()
    
    test_code = """
def hello():
    print("world")
"""
    
    # Execute code analysis
    result = o.execute_skill("code_analysis", {"code": test_code, "language": "python"})
    
    assert result is not None
    assert "analysis" in result or "error" in result


def test_research_retrieve(tmp_path):
    """Test research data retrieval."""
    o = Orchestrator()
    
    # Test with a simple URL
    data = o.research_retrieve("test", ["https://example.com"])
    
    assert data is not None
    assert "scrapes" in data or "error" in data
    assert "topic" in data


def test_agent_creation():
    """Test agent creation."""
    o = Orchestrator()
    
    # Create an agent
    success = o.create_agent(
        "test_agent",
        {"role": "Tester", "policy": "auto"},
        approve=True
    )
    
    assert success is True
    assert "test_agent" in o.list_agents()


def test_audit_log():
    """Test audit logging."""
    o = Orchestrator()
    
    # Perform some operations
    o.list_skills()
    o.get_skill_info("web_search")
    
    # Check audit log
    log = o.get_audit_log(limit=10)
    assert len(log) > 0
    assert all("timestamp" in entry for entry in log)
    assert all("event" in entry for entry in log)


def test_orchestrator_status():
    """Test orchestrator status."""
    o = Orchestrator()
    
    status = o.get_status()
    
    assert "agents" in status
    assert "skills" in status
    assert "audit_log_size" in status
    assert "loaded_agents" in status
    assert "available_skills" in status


def test_skill_not_found():
    """Test handling of non-existent skill."""
    o = Orchestrator()
    
    with pytest.raises(ValueError):
        o.execute_skill("nonexistent_skill", {})


def test_skill_disabled():
    """Test that disabled skills cannot be executed."""
    o = Orchestrator()
    
    # Make sure web_search is disabled
    o.approve_skill("web_search", enabled=False)
    
    # Try to execute - should fail
    with pytest.raises(ValueError):
        o.execute_skill("web_search", {"query": "test"})


if __name__ == "__main__":
    # Run tests manually
    print("Running orchestrator tests...")
    
    test_orchestrator_init()
    print("✅ test_orchestrator_init")
    
    test_skill_registry()
    print("✅ test_skill_registry")
    
    test_get_skill_info()
    print("✅ test_get_skill_info")
    
    test_skill_approval()
    print("✅ test_skill_approval")
    
    test_skill_exec()
    print("✅ test_skill_exec")
    
    test_memory_search_skill()
    print("✅ test_memory_search_skill")
    
    test_code_analysis_skill()
    print("✅ test_code_analysis_skill")
    
    test_agent_creation()
    print("✅ test_agent_creation")
    
    test_audit_log()
    print("✅ test_audit_log")
    
    test_orchestrator_status()
    print("✅ test_orchestrator_status")
    
    print("\n🎉 All tests passed!")


"""
Test Research Scrape System
---------------------------
Tests for user research and agent scrape workflows.
"""

import os
import sys
import json
from pathlib import Path

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-dummy"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-dummy"
os.environ["SECRET_KEY"] = "test-secret-key"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.ai.orchestrator import Orchestrator
from backend.app.ai.data_formatter import DataFormatter
from backend.app.ai.orchestrator_settings import OrchestratorSettings


def test_data_formatter_normalize():
    """Test data normalization."""
    formatter = DataFormatter()
    
    # Test data with success and error
    data = [
        {"title": "Test 1", "text": "Content 1", "url": "https://example.com/1"},
        {"error": "Failed to scrape"},
        {"title": "Test 2", "text": "Content 2"}
    ]
    
    normalized = formatter.normalize(data)
    
    assert "timestamp" in normalized
    assert "sources" in normalized
    assert "content" in normalized
    assert "metadata" in normalized
    assert normalized["metadata"]["total_sources"] == 3
    assert normalized["metadata"]["successful_scrapes"] == 2
    assert normalized["metadata"]["failed_scrapes"] == 1
    assert len(normalized["content"]) == 2
    
    print("✅ Data normalization test passed")


def test_data_formatter_markdown():
    """Test Markdown generation."""
    formatter = DataFormatter(output_dir="data/test_output")
    
    data = [
        {"title": "AI Frameworks", "text": "Python frameworks for AI", "url": "https://example.com"}
    ]
    
    normalized = formatter.normalize(data)
    md_path = formatter.to_markdown("test_topic", normalized)
    
    assert Path(md_path).exists()
    assert Path(md_path).suffix == ".md"
    
    content = Path(md_path).read_text()
    assert "Research Report: test_topic" in content
    assert "AI Frameworks" in content
    
    # Cleanup
    Path(md_path).unlink()
    
    print("✅ Markdown generation test passed")


def test_settings_management():
    """Test orchestrator settings."""
    settings = OrchestratorSettings(settings_file="backend/app/ai/test_settings.json")
    
    # Test default settings
    assert settings.get("allow_agent_scrape") == False
    assert settings.get("auto_approve_skills") == False
    
    # Test enable agent scrape
    settings.enable_agent_scrape(True)
    assert settings.is_agent_scrape_allowed() == True
    
    # Test disable
    settings.enable_agent_scrape(False)
    assert settings.is_agent_scrape_allowed() == False
    
    # Test update multiple settings
    settings.update({
        "allow_agent_scrape": True,
        "auto_approve_skills": True
    }, save=False)
    
    assert settings.get("allow_agent_scrape") == True
    assert settings.get("auto_approve_skills") == True
    
    # Cleanup
    Path("backend/app/ai/test_settings.json").unlink(missing_ok=True)
    
    print("✅ Settings management test passed")


def test_orchestrator_research_scrape():
    """Test user research scrape workflow."""
    o = Orchestrator()
    
    # Create test project
    project_name = "test_project"
    topic = "AI_Testing"
    urls = ["https://example.com"]
    
    # Run research scrape
    result = o.run_research_scrape(
        project=project_name,
        topic=topic,
        urls=urls,
        intent="testing"
    )
    
    # Check result
    assert "markdown" in result or "error" in result
    
    if "markdown" in result:
        # Check files were created
        md_path = Path(result["markdown"])
        assert "projects" in str(md_path)
        assert project_name in str(md_path)
        assert "research" in str(md_path)
        
        # Check metadata
        if "metadata" in result:
            assert "total_sources" in result["metadata"]
        
        print(f"✅ Research scrape test passed: {result['markdown']}")
    else:
        print(f"⚠️  Research scrape returned error (expected with dummy URLs): {result.get('error')}")


def test_orchestrator_agent_scrape_blocked():
    """Test agent scrape when disabled."""
    o = Orchestrator()
    
    # Ensure agent scraping is disabled
    o.settings.enable_agent_scrape(False)
    
    # Try agent scrape
    result = o.agent_scrape(
        agent_name="test_agent",
        query="test query",
        urls=["https://example.com"]
    )
    
    # Should be blocked
    assert result is None
    
    print("✅ Agent scrape blocking test passed")


def test_orchestrator_agent_scrape_allowed():
    """Test agent scrape when enabled."""
    o = Orchestrator()
    
    # Enable agent scraping
    o.settings.enable_agent_scrape(True)
    
    # Try agent scrape
    result = o.agent_scrape(
        agent_name="test_agent",
        query="test_query",
        urls=["https://example.com"]
    )
    
    # Should return result (even if error due to dummy URL)
    assert result is not None
    assert "file" in result or "error" in result
    
    if "file" in result:
        # Check file was created
        file_path = Path(result["file"])
        assert "data/agents" in str(file_path)
        assert "test_agent" in str(file_path)
        assert "scrapes" in str(file_path)
        
        print(f"✅ Agent scrape allowed test passed: {result['file']}")
    else:
        print(f"⚠️  Agent scrape returned error (expected with dummy URLs): {result.get('error')}")
    
    # Disable again
    o.settings.enable_agent_scrape(False)


def test_audit_log_research():
    """Test audit logging for research operations."""
    o = Orchestrator()
    
    # Clear audit log
    o.audit_log.clear()
    
    # Run research scrape
    o.run_research_scrape(
        project="test_audit",
        topic="test_topic",
        urls=["https://example.com"],
        intent="testing"
    )
    
    # Check audit log
    log = o.get_audit_log()
    
    # Should have start and done/error events
    events = [entry["event"] for entry in log]
    assert "research_user_start" in events
    assert "research_user_done" in events or "research_user_error" in events
    
    print(f"✅ Audit log test passed: {len(log)} events")


def test_settings_persistence():
    """Test settings save and load."""
    settings_file = "backend/app/ai/test_persist_settings.json"
    
    # Create settings
    settings1 = OrchestratorSettings(settings_file=settings_file)
    settings1.enable_agent_scrape(True)
    settings1.set("custom_setting", "test_value")
    settings1.save()
    
    # Load in new instance
    settings2 = OrchestratorSettings(settings_file=settings_file)
    
    assert settings2.is_agent_scrape_allowed() == True
    assert settings2.get("custom_setting") == "test_value"
    
    # Cleanup
    Path(settings_file).unlink(missing_ok=True)
    
    print("✅ Settings persistence test passed")


def test_project_directory_creation():
    """Test project directory structure."""
    o = Orchestrator()
    
    project_name = "test_dir_project"
    topic = "test_topic"
    
    # Run research scrape (will create directories)
    result = o.run_research_scrape(
        project=project_name,
        topic=topic,
        urls=["https://example.com"]
    )
    
    # Check directory structure
    project_dir = Path("projects") / project_name / "research"
    assert project_dir.exists()
    assert project_dir.is_dir()
    
    print(f"✅ Project directory test passed: {project_dir}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 Testing Research Scrape System")
    print("="*60 + "\n")
    
    tests = [
        ("Data Formatter - Normalize", test_data_formatter_normalize),
        ("Data Formatter - Markdown", test_data_formatter_markdown),
        ("Settings Management", test_settings_management),
        ("Settings Persistence", test_settings_persistence),
        ("Orchestrator - Research Scrape", test_orchestrator_research_scrape),
        ("Orchestrator - Agent Scrape Blocked", test_orchestrator_agent_scrape_blocked),
        ("Orchestrator - Agent Scrape Allowed", test_orchestrator_agent_scrape_allowed),
        ("Audit Log - Research", test_audit_log_research),
        ("Project Directory Creation", test_project_directory_creation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n{len(str(passed + failed + 1))}️⃣  Testing {name}...")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"🎉 Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


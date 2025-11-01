#!/usr/bin/env python3
"""
Orchestrator Demo
-----------------
Demonstrates the orchestrator system with skill approval workflow.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/ai"


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_orchestrator_status():
    """Demo: Get orchestrator status."""
    print_section("1. Orchestrator Status")
    
    response = requests.get(f"{BASE_URL}/orchestrator/status")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def demo_list_skills():
    """Demo: List all skills."""
    print_section("2. List Skills")
    
    response = requests.get(f"{BASE_URL}/orchestrator/skills")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['count']} skills:")
    for skill in data['skills']:
        print(f"  - {skill}")


def demo_skill_info():
    """Demo: Get skill information."""
    print_section("3. Skill Information")
    
    skill_name = "web_search"
    response = requests.get(f"{BASE_URL}/orchestrator/skills/{skill_name}")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"\nSkill: {data['name']}")
    print(f"Version: {data['version']}")
    print(f"Description: {data['description']}")
    print(f"Enabled: {data['enabled']}")
    print(f"Category: {data['category']}")
    print(f"Permissions: {data['permissions']}")


def demo_disabled_skill_execution():
    """Demo: Try to execute a disabled skill."""
    print_section("4. Execute Disabled Skill (Should Fail)")
    
    response = requests.post(
        f"{BASE_URL}/orchestrator/skills/execute",
        json={
            "skill_name": "web_search",
            "parameters": {
                "query": "FastAPI best practices",
                "num_results": 3
            }
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")


def demo_request_approval():
    """Demo: Request approval for a skill."""
    print_section("5. Request Skill Approval")
    
    response = requests.post(
        f"{BASE_URL}/approvals/request",
        json={
            "item_type": "skill",
            "item_name": "web_search",
            "config": {
                "name": "web_search",
                "version": "1.0.0",
                "enabled": True
            },
            "reason": "Need web search for research tasks"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    return data.get("request_id")


def demo_list_pending_approvals():
    """Demo: List pending approvals."""
    print_section("6. List Pending Approvals")
    
    response = requests.get(f"{BASE_URL}/approvals/pending")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['count']} pending approvals:")
    for approval in data['pending']:
        print(f"\n  ID: {approval['id']}")
        print(f"  Type: {approval['type']}")
        print(f"  Name: {approval['name']}")
        print(f"  Reason: {approval['reason']}")
        print(f"  Status: {approval['status']}")


def demo_approve_request(request_id):
    """Demo: Approve a request."""
    print_section("7. Approve Request")
    
    response = requests.post(
        f"{BASE_URL}/approvals/{request_id}/approve",
        json={
            "approver": "demo_user"
        }
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def demo_execute_approved_skill():
    """Demo: Execute an approved skill."""
    print_section("8. Execute Approved Skill")
    
    # First reload skills to pick up the enabled status
    requests.post(f"{BASE_URL}/orchestrator/skills/reload")
    
    response = requests.post(
        f"{BASE_URL}/orchestrator/skills/execute",
        json={
            "skill_name": "web_search",
            "parameters": {
                "query": "Python async programming",
                "num_results": 3
            }
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nSkill: {data['skill']}")
        print(f"Status: {data['status']}")
        print(f"\nResults:")
        for i, result in enumerate(data.get('result', []), 1):
            print(f"\n  {i}. {result.get('title', 'N/A')}")
            print(f"     {result.get('snippet', 'N/A')[:100]}...")
    else:
        print(f"Error: {response.text}")


def demo_memory_search_skill():
    """Demo: Execute memory search skill."""
    print_section("9. Memory Search Skill")
    
    # First insert some test data into memory
    print("Inserting test data into memory...")
    requests.post(
        f"{BASE_URL}/memory/insert",
        json={
            "text": "User prefers dark mode and Python programming",
            "metadata": {"category": "preferences"}
        }
    )
    
    time.sleep(1)  # Give memory system time to process
    
    # Now search memory
    response = requests.post(
        f"{BASE_URL}/orchestrator/skills/execute",
        json={
            "skill_name": "memory_search",
            "parameters": {
                "query": "user preferences",
                "k": 5
            }
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nSkill: {data['skill']}")
        print(f"Status: {data['status']}")
        print(f"\nFound {len(data.get('result', []))} memories")
    else:
        print(f"Error: {response.text}")


def demo_code_analysis_skill():
    """Demo: Execute code analysis skill."""
    print_section("10. Code Analysis Skill")
    
    test_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""
    
    response = requests.post(
        f"{BASE_URL}/orchestrator/skills/execute",
        json={
            "skill_name": "code_analysis",
            "parameters": {
                "code": test_code,
                "language": "python"
            }
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nSkill: {data['skill']}")
        print(f"Status: {data['status']}")
        print(f"\nAnalysis:")
        print(data['result'].get('analysis', 'N/A')[:500])
    else:
        print(f"Error: {response.text}")


def demo_audit_log():
    """Demo: Get audit log."""
    print_section("11. Audit Log")
    
    response = requests.get(f"{BASE_URL}/orchestrator/audit-log?limit=10")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"\nRecent {data['count']} events:")
    for entry in data['entries'][-5:]:  # Show last 5
        print(f"\n  {entry['timestamp']}")
        print(f"  Event: {entry['event']}")
        print(f"  Data: {entry['data']}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("  ORCHESTRATOR SYSTEM DEMO")
    print("  Make sure the backend is running on http://localhost:8000")
    print("="*60)
    
    try:
        # Check if backend is running
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code != 200:
            print("\n❌ Backend not responding. Please start the backend first:")
            print("   cd backend && uvicorn main:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend. Please start it first:")
        print("   cd backend && uvicorn main:app --reload")
        return
    
    # Run demos
    demo_orchestrator_status()
    demo_list_skills()
    demo_skill_info()
    demo_disabled_skill_execution()
    
    # Approval workflow
    request_id = demo_request_approval()
    demo_list_pending_approvals()
    
    if request_id:
        demo_approve_request(request_id)
        time.sleep(1)  # Give system time to process
        demo_execute_approved_skill()
    
    # Other skills
    demo_memory_search_skill()
    demo_code_analysis_skill()
    
    # Audit log
    demo_audit_log()
    
    print("\n" + "="*60)
    print("  DEMO COMPLETE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()


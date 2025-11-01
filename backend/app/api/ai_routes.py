"""
AI API Routes
-------------
Endpoints for AI and multi-agent functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from backend.app.ai import AI_REGISTRY
from backend.app.ai.llm_service import llm_service
from backend.app.ai.memory_system import memory_system
from backend.app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/ai", tags=["AI"])


# === Request/Response Models ===

class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str


class ChatHistoryRequest(BaseModel):
    messages: List[Dict[str, str]]
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


class FrameworkStatusResponse(BaseModel):
    category: str
    frameworks: List[str]
    count: int


class AIStatusResponse(BaseModel):
    total_frameworks: int
    categories: List[FrameworkStatusResponse]


# === Endpoints ===

@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status():
    """
    Get status of all AI frameworks.
    
    Returns:
        Status of all loaded AI frameworks by category
    """
    categories = []
    total = 0
    
    for category, frameworks in AI_REGISTRY.items():
        framework_names = list(frameworks.keys())
        categories.append(
            FrameworkStatusResponse(
                category=category,
                frameworks=framework_names,
                count=len(framework_names)
            )
        )
        total += len(framework_names)
    
    return AIStatusResponse(
        total_frameworks=total,
        categories=categories
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with an LLM.
    
    Args:
        request: Chat request with message and optional provider/model
        
    Returns:
        LLM response
    """
    try:
        response = llm_service.chat(
            message=request.message,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(
            response=response,
            provider=request.provider or "openai",
            model=request.model or "gpt-4"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@router.post("/chat/history", response_model=ChatResponse)
async def chat_with_history(request: ChatHistoryRequest):
    """
    Chat with conversation history.
    
    Args:
        request: Chat request with message history
        
    Returns:
        LLM response
    """
    try:
        response = llm_service.chat_with_history(
            messages=request.messages,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(
            response=response,
            provider=request.provider or "openai",
            model=request.model or "gpt-4"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")


@router.get("/frameworks")
async def list_frameworks():
    """
    List all available AI frameworks.
    
    Returns:
        Dictionary of all loaded frameworks by category
    """
    return {
        category: list(frameworks.keys())
        for category, frameworks in AI_REGISTRY.items()
    }


@router.get("/frameworks/{category}")
async def get_frameworks_by_category(category: str):
    """
    Get frameworks in a specific category.
    
    Args:
        category: Framework category (core, multi_agents, enterprise, transformers)
        
    Returns:
        List of frameworks in the category
    """
    if category not in AI_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available: {list(AI_REGISTRY.keys())}"
        )
    
    return {
        "category": category,
        "frameworks": list(AI_REGISTRY[category].keys()),
        "count": len(AI_REGISTRY[category])
    }


@router.get("/health")
async def ai_health_check():
    """
    Health check for AI services.

    Returns:
        Health status of AI frameworks
    """
    total_frameworks = sum(len(frameworks) for frameworks in AI_REGISTRY.values())

    return {
        "status": "healthy" if total_frameworks > 0 else "degraded",
        "total_frameworks": total_frameworks,
        "categories": {
            category: len(frameworks)
            for category, frameworks in AI_REGISTRY.items()
        }
    }


# === Memory System Endpoints ===

class MemoryInsertRequest(BaseModel):
    text: str
    sets: Optional[List[str]] = None
    meta: Optional[Dict] = None
    pin: bool = False
    title: str = ""


class MemoryTeachRequest(BaseModel):
    text: str
    sets: Optional[List[str]] = None
    title: str = ""


class MemoryRecallRequest(BaseModel):
    query: str
    k: int = 10
    sets_filter: Optional[List[str]] = None


class MemoryInsertResponse(BaseModel):
    id: str
    status: str


class MemoryRecallResponse(BaseModel):
    results: List[Dict]
    count: int


@router.post("/memory/insert", response_model=MemoryInsertResponse)
async def memory_insert(request: MemoryInsertRequest):
    """
    Insert a memory into the system.

    Args:
        request: Memory insertion request

    Returns:
        Memory ID
    """
    try:
        rid = memory_system.insert(
            text=request.text,
            sets=request.sets,
            meta=request.meta,
            pin=request.pin,
            title=request.title
        )
        return MemoryInsertResponse(id=rid, status="inserted")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory insert error: {str(e)}")


@router.post("/memory/teach", response_model=MemoryInsertResponse)
async def memory_teach(request: MemoryTeachRequest):
    """
    Teach the system important information (high-priority memory).

    Args:
        request: Memory teach request

    Returns:
        Memory ID
    """
    try:
        rid = memory_system.teach(
            text=request.text,
            sets=request.sets,
            title=request.title
        )
        return MemoryInsertResponse(id=rid, status="taught")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory teach error: {str(e)}")


@router.post("/memory/recall", response_model=MemoryRecallResponse)
async def memory_recall(request: MemoryRecallRequest):
    """
    Recall memories based on a query.

    Args:
        request: Memory recall request

    Returns:
        List of relevant memories
    """
    try:
        results = memory_system.recall(
            query=request.query,
            k=request.k,
            sets_filter=request.sets_filter
        )
        return MemoryRecallResponse(results=results, count=len(results))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory recall error: {str(e)}")


@router.post("/memory/tick")
async def memory_tick():
    """
    Run memory consolidation (promote short-term to mid-term).

    Returns:
        Status message
    """
    try:
        memory_system.tick()
        return {"status": "ok", "message": "Memory consolidation completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory tick error: {str(e)}")


@router.get("/memory/validate/{memory_id}")
async def memory_validate(memory_id: str):
    """
    Validate a memory's semantic integrity.

    Args:
        memory_id: Memory ID to validate

    Returns:
        Validation result
    """
    try:
        is_valid = memory_system.validate(memory_id)
        return {
            "id": memory_id,
            "valid": is_valid,
            "status": "valid" if is_valid else "invalid"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory validation error: {str(e)}")


# === Orchestrator Endpoints ===

class AgentCreateRequest(BaseModel):
    name: str
    config: Dict
    approve: bool = False


class SkillExecuteRequest(BaseModel):
    skill_name: str
    parameters: Dict


@router.get("/orchestrator/status")
async def orchestrator_status():
    """
    Get orchestrator status.

    Returns:
        Orchestrator status
    """
    return orchestrator.get_status()


@router.get("/orchestrator/agents")
async def list_agents():
    """
    List all loaded agents.

    Returns:
        List of agent names
    """
    return {
        "agents": orchestrator.list_agents(),
        "count": len(orchestrator.list_agents())
    }


@router.post("/orchestrator/agents")
async def create_agent(request: AgentCreateRequest):
    """
    Create a new agent.

    Args:
        request: Agent creation request

    Returns:
        Creation result
    """
    try:
        created = orchestrator.create_agent(
            name=request.name,
            config=request.config,
            approve=request.approve
        )
        return {
            "name": request.name,
            "created": created,
            "status": "created" if created else "pending_approval"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent creation error: {str(e)}")


@router.delete("/orchestrator/agents/{agent_name}")
async def destroy_agent(agent_name: str):
    """
    Destroy an agent.

    Args:
        agent_name: Agent name

    Returns:
        Destruction result
    """
    try:
        orchestrator.destroy_agent(agent_name)
        return {
            "name": agent_name,
            "status": "destroyed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent destruction error: {str(e)}")


@router.get("/orchestrator/skills")
async def list_skills():
    """
    List all available skills.

    Returns:
        List of skills
    """
    skills = orchestrator.list_skills()
    return {
        "skills": skills,
        "count": len(skills)
    }


@router.get("/orchestrator/skills/{skill_name}")
async def get_skill_info(skill_name: str):
    """
    Get skill information.

    Args:
        skill_name: Skill name

    Returns:
        Skill configuration
    """
    skill_info = orchestrator.skill_registry.get_skill(skill_name)
    if not skill_info:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
    return skill_info


@router.post("/orchestrator/skills/execute")
async def execute_skill(request: SkillExecuteRequest):
    """
    Execute a skill.

    Args:
        request: Skill execution request

    Returns:
        Skill execution result
    """
    try:
        skill = orchestrator.load_skill(request.skill_name)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill '{request.skill_name}' not found")

        result = skill.execute(**request.parameters)
        return {
            "skill": request.skill_name,
            "result": result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill execution error: {str(e)}")


@router.post("/orchestrator/skills/reload")
async def reload_skills():
    """
    Reload all skills from disk.

    Returns:
        Reload result
    """
    try:
        orchestrator.skill_registry.reload()
        return {
            "status": "reloaded",
            "skills": orchestrator.list_skills(),
            "count": len(orchestrator.list_skills())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill reload error: {str(e)}")


@router.get("/orchestrator/audit-log")
async def get_audit_log(limit: int = 100):
    """
    Get orchestrator audit log.

    Args:
        limit: Maximum number of entries

    Returns:
        Audit log entries
    """
    return {
        "entries": orchestrator.get_audit_log(limit=limit),
        "count": len(orchestrator.get_audit_log(limit=limit))
    }


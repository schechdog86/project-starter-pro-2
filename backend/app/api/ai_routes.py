"""
AI API Routes
-------------
Endpoints for AI and multi-agent functionality.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
from backend.app.core.config import settings
from backend.app.ai import AI_REGISTRY
from backend.app.ai.llm_service import llm_service
from backend.app.ai.memory_system import memory_system
from backend.app.ai.orchestrator import orchestrator
from backend.app.skills.approval import approval_manager
from backend.app.ai.memory_adapter import UnifiedMemoryAdapter


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
    # Project-aware RAG options
    project: Optional[str] = None
    category: Optional[str] = None
    context_k: int = 8


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
        if request.project:
            response = orchestrator.chat_with_history_for_project(
                project=request.project,
                messages=request.messages,
                provider=request.provider,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                k=request.context_k,
                category=request.category,
            )
        else:
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


class SkillAddRequest(BaseModel):
    name: str
    config: Dict
    code: str
    enabled: bool = False


class SkillApproveRequest(BaseModel):
    enabled: bool = True


class SkillExecParamsRequest(BaseModel):
    params: Dict[str, Any] = {}


class SkillGenerateRequest(BaseModel):
    name: str
    prompt: str


class ProjectRequest(BaseModel):
    name: str


class ResearchRequest(BaseModel):
    topic: str
    urls: List[str]


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


@router.post("/skills")
async def add_skill(request: SkillAddRequest):
    """
    Add a new skill with config and code.

    Args:
        request: Skill add request

    Returns:
        Success status
    """
    try:
        orchestrator.add_skill(request.name, request.config, request.code)

        # If enabled, approve it
        if request.enabled:
            orchestrator.approve_skill(request.name, enabled=True)

        return {"ok": True, "name": request.name, "enabled": request.enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill add error: {str(e)}")


@router.post("/skills/{name}/approve")
async def approve_skill_endpoint(name: str, request: SkillApproveRequest):
    """
    Approve and enable a skill.

    Args:
        name: Skill name
        request: Approval request

    Returns:
        Success status
    """
    try:
        success = orchestrator.approve_skill(name, enabled=request.enabled)
        if not success:
            raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")

        return {"ok": True, "name": name, "enabled": request.enabled}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill approval error: {str(e)}")


@router.post("/skills/{name}/execute")
async def execute_skill_by_name(name: str, request: SkillExecParamsRequest):
    """
    Execute a skill by name with parameters.

    Args:
        name: Skill name
        request: Execution parameters

    Returns:
        Execution result
    """
    try:
        result = orchestrator.execute_skill(name, request.params)
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/skills/generate")
async def generate_skill(request: SkillGenerateRequest):
    """
    Generate a new skill from a prompt.

    Args:
        request: Skill generation request

    Returns:
        Generated skill draft
    """
    try:
        result = orchestrator.generate_skill_from_prompt(request.name, request.prompt)
        return {"ok": True, "draft": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill generation error: {str(e)}")


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


# === Approval System Endpoints ===

class ApprovalRequest(BaseModel):
    item_type: str
    item_name: str
    config: Dict
    reason: str = ""


class ApprovalActionRequest(BaseModel):
    approver: str = "user"


class RejectionRequest(BaseModel):
    reason: str = ""
    rejector: str = "user"


@router.get("/approvals/pending")
async def get_pending_approvals():
    """
    Get all pending approval requests.

    Returns:
        List of pending approvals
    """
    pending = approval_manager.get_pending()
    return {
        "pending": pending,
        "count": len(pending)
    }


@router.get("/approvals/{request_id}")
async def get_approval_request(request_id: str):
    """
    Get a specific approval request.

    Args:
        request_id: Approval request ID

    Returns:
        Approval request details
    """
    request = approval_manager.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail=f"Approval request '{request_id}' not found")
    return request


@router.post("/approvals/request")
async def request_approval(request: ApprovalRequest):
    """
    Request approval for a skill or agent.

    Args:
        request: Approval request

    Returns:
        Approval request ID
    """
    try:
        request_id = approval_manager.request_approval(
            item_type=request.item_type,
            item_name=request.item_name,
            config=request.config,
            reason=request.reason
        )
        return {
            "request_id": request_id,
            "status": "pending",
            "message": "Approval requested"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval request error: {str(e)}")


@router.post("/approvals/{request_id}/approve")
async def approve_request(request_id: str, request: ApprovalActionRequest):
    """
    Approve a pending request.

    Args:
        request_id: Approval request ID
        request: Approval action details

    Returns:
        Approval result
    """
    try:
        success = approval_manager.approve(request_id, approver=request.approver)
        if not success:
            raise HTTPException(status_code=404, detail=f"Approval request '{request_id}' not found")

        # Get the approved item
        approved_item = approval_manager.get_request(request_id)

        # If it's a skill, enable it
        if approved_item["type"] == "skill":
            skill_name = approved_item["name"]
            config = approved_item["config"]
            config["enabled"] = True

            # Update config file
            from pathlib import Path
            import json
            skill_path = Path(__file__).parent.parent / "skills" / skill_name / "config.json"
            if skill_path.exists():
                skill_path.write_text(json.dumps(config, indent=2))
                orchestrator.skill_registry.reload()

        return {
            "request_id": request_id,
            "status": "approved",
            "approved_by": request.approver,
            "message": "Request approved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval error: {str(e)}")


@router.post("/approvals/{request_id}/reject")
async def reject_request(request_id: str, request: RejectionRequest):
    """
    Reject a pending request.

    Args:
        request_id: Approval request ID
        request: Rejection details

    Returns:
        Rejection result
    """
    try:
        success = approval_manager.reject(
            request_id,
            reason=request.reason,
            rejector=request.rejector
        )
        if not success:
            raise HTTPException(status_code=404, detail=f"Approval request '{request_id}' not found")

        return {
            "request_id": request_id,
            "status": "rejected",
            "rejected_by": request.rejector,
            "reason": request.reason,
            "message": "Request rejected"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rejection error: {str(e)}")


# === Project Management Endpoints ===

@router.post("/projects/run")
async def run_project(request: ProjectRequest):
    """
    Run a project through document flow.

    Args:
        request: Project request

    Returns:
        Project result
    """
    try:
        result = orchestrator.run_project(request.name)
        return {"ok": True, "project": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{name}/status")
async def project_status(name: str):
    """
    Get project status from orchestrator's document flow persistence.

    Args:
        name: Project name

    Returns:
        Project status (phase, next_required_doc, docs_status, updated_at)
    """
    try:
        status = orchestrator.get_project_status(name)
        if not status:
            raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
        return {"project": status}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load project status")


# === Research & Data Retrieval Endpoints ===

@router.post("/research/retrieve")
async def research_retrieve(request: ResearchRequest):
    """
    Retrieve research data from URLs.

    Args:
        request: Research request

    Returns:
        Research data
    """
    try:
        result = orchestrator.research_retrieve(request.topic, request.urls)
        return {"ok": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research retrieval error: {str(e)}")


# === User Research Scrape Endpoints ===

class ResearchRunRequest(BaseModel):
    """Request model for user research scrape."""
    project: str
    topic: str
    urls: List[str]
    intent: str = "general"


@router.post("/research/user")
async def run_user_research(request: ResearchRunRequest):
    """
    Run user-approved research scrape for project reports.

    This endpoint:
    1. Scrapes data from provided URLs
    2. Generates Markdown and PDF reports
    3. Saves to project folder
    4. Stores in memory system

    Args:
        request: Research run request with project, topic, urls, intent

    Returns:
        Paths to generated Markdown and PDF files
    """
    try:
        result = orchestrator.run_research_scrape(
            request.project,
            request.topic,
            request.urls,
            intent=request.intent
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research scrape error: {str(e)}")


# === Agent Scrape Endpoints ===

class AgentScrapeRequest(BaseModel):
    """Request model for agent scrape."""
    agent_name: str
    query: str
    urls: List[str]


@router.post("/agents/scrape")
async def run_agent_scrape(request: AgentScrapeRequest):
    """
    Run background agent scrape (requires settings permission).

    This endpoint allows agents to autonomously gather data,
    but only if enabled in orchestrator settings.

    Args:
        request: Agent scrape request with agent_name, query, urls

    Returns:
        Path to saved data file, or error if not allowed
    """
    try:
        result = orchestrator.agent_scrape(
            request.agent_name,
            request.query,
            request.urls
        )

        if result is None:
            raise HTTPException(
                status_code=403,
                detail="Agent scraping is disabled. Enable in settings: allow_agent_scrape=true"
            )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {"ok": True, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent scrape error: {str(e)}")


# === Settings Endpoints ===

class SettingsUpdateRequest(BaseModel):
    """Request model for settings update."""
    settings: Dict[str, Any]


@router.get("/settings")
async def get_settings():
    """
    Get all orchestrator settings.

    Returns:
        Current settings
    """
    try:
        settings = orchestrator.settings.get_all()
        return {"ok": True, "settings": settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings error: {str(e)}")


@router.post("/settings")
async def update_settings(request: SettingsUpdateRequest):
    """
    Update orchestrator settings.

    Args:
        request: Settings update request

    Returns:
        Updated settings
    """
    try:
        success = orchestrator.settings.update(request.settings, save=True)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save settings")

        return {"ok": True, "settings": orchestrator.settings.get_all()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings update error: {str(e)}")


@router.post("/settings/agent-scrape")
async def toggle_agent_scrape(enabled: bool = True):
    """
    Enable or disable agent scraping.

    Args:
        enabled: Whether to enable agent scraping

    Returns:
        Updated setting
    """
    try:
        success = orchestrator.settings.enable_agent_scrape(enabled)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update setting")

        return {
            "ok": True,
            "allow_agent_scrape": orchestrator.settings.is_agent_scrape_allowed()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings error: {str(e)}")


# === Project RAG Endpoints ===

class RagAddRequest(BaseModel):
    content: Optional[str] = None
    src_path: Optional[str] = None
    filename: Optional[str] = None
    category: str = "docs"


class RagIngestRequest(BaseModel):
    categories: Optional[List[str]] = None


@router.post("/projects/{name}/rag/add")
async def project_rag_add(name: str, request: RagAddRequest):
    """
    Add content or copy a file into the project's RAG store and index it.
    - If content provided, write to docs/<category>/<filename or auto>.md and index.
    - If src_path provided, copy from data/imports/... into project and index.
    """
    try:
        rag = UnifiedMemoryAdapter(name)
        if request.content:
            fname = request.filename or "snippet.md"
            dst = rag.docs_dir / request.category / fname
            dst.write_text(request.content, encoding="utf-8")
            rid = rag.add_text(request.content, title=fname, category=request.category, meta={"path": str(dst)})
            return {"ok": True, "id": rid, "path": str(dst)}
        elif request.src_path:
            rid = rag.add_file(request.src_path, filename=request.filename, category=request.category)
            return {"ok": True, "id": rid}
        else:
            raise HTTPException(status_code=400, detail="Provide either 'content' or 'src_path'")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG add error: {str(e)}")


@router.post("/projects/{name}/rag/ingest")
async def project_rag_ingest(name: str, request: RagIngestRequest):
    """Ingest all eligible files from the project's docs folders into its RAG DB."""
    try:
        rag = UnifiedMemoryAdapter(name)
        count = rag.ingest_project_docs(categories=request.categories)
        return {"ok": True, "ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG ingest error: {str(e)}")


@router.get("/projects/{name}/rag/search")
async def project_rag_search(name: str, q: str, k: int = 10, category: Optional[str] = None):
    """Search the project's RAG DB."""
    try:
        rag = UnifiedMemoryAdapter(name)
        results = rag.search(q, k=k, category=category)
        return {"ok": True, "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")



# === LLM Providers/Models Endpoints ===

@router.get("/llm/providers")
async def llm_providers():
    """Return available LLM providers (filtered by configured API keys if present)."""
    try:
        providers = []
        if settings.OPENAI_API_KEY:
            providers.append("openai")
        if settings.ANTHROPIC_API_KEY or settings.CLAUDE_API_KEY:
            providers.append("anthropic")
        if settings.DEEPSEEK_API_KEY:
            providers.append("deepseek")
        if not providers:
            providers = ["openai", "anthropic", "deepseek"]
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Providers error: {str(e)}")


@router.get("/llm/models/{provider}")
async def llm_models(provider: str):
    """Return supported models for a provider (static curated list)."""
    try:
        p = (provider or "").lower()
        mapping = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku"],
            "deepseek": ["deepseek-chat", "deepseek-coder"],
        }
        return {"provider": p, "models": mapping.get(p, ["gpt-3.5-turbo"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Models error: {str(e)}")


# === Project Docs Upload/List + RAG Upload ===

@router.post("/projects/{name}/rag/upload")
async def project_rag_upload(name: str, category: str = Form("docs"), file: UploadFile = File(...)):
    """Upload a file to data/imports/{project}/{category} then index into project RAG."""
    try:
        rag = UnifiedMemoryAdapter(name)
        base = Path("data/imports") / name / category
        base.mkdir(parents=True, exist_ok=True)
        safe_name = Path(file.filename).name
        dst = base / safe_name
        content = await file.read()
        with open(dst, "wb") as f:
            f.write(content)
        rid = rag.add_file(str(dst), filename=safe_name, category=category)
        return {"ok": True, "id": rid, "filename": safe_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.get("/projects/{name}/docs/list")
async def project_docs_list(name: str, category: str = "docs"):
    """List files in data/projects/{project}/docs/{category}."""
    try:
        base = Path("data/projects") / name / "docs" / category
        items = []
        if base.exists() and base.is_dir():
            for p in sorted(base.iterdir()):
                if p.is_file():
                    stat = p.stat()
                    items.append({
                        "name": p.name,
                        "path": str(p),
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                    })
        return {"ok": True, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Docs list error: {str(e)}")



"""
AI Initialization Manager
-------------------------
Auto-detects and initializes all supported AI frameworks.

Supports:
- Core AI frameworks (LangChain, LlamaIndex, Haystack, LiteLLM, ScrapeGraph)
- Multi-agent systems (AutoGen, CrewAI, LangGraph, Swarm, MetaGPT, SuperAGI, TaskWeaver, AtomicAgents, SmolAgents)
- Enterprise frameworks (Semantic Kernel, Rasa)
- Transformer and vector ecosystems (HuggingFace, ChromaDB, Pinecone, Weaviate, Milvus)
"""

import importlib
import logging
from backend.app.core.config import settings

logger = logging.getLogger("ai_init")
logger.setLevel(logging.INFO)


def try_import(package):
    """Safely import a module, return None if not installed."""
    try:
        return importlib.import_module(package)
    except ImportError:
        logger.info(f"[❌] {package} not installed, skipping.")
        return None


def init_core_ai():
    """Initialize core AI libraries."""
    ai = {}

    langchain = try_import("langchain")
    llama_index = try_import("llama_index")
    haystack = try_import("haystack")
    litellm = try_import("litellm")
    scrapegraph = try_import("scrapegraph_ai")

    if langchain:
        ai["langchain"] = langchain
        logger.info("[✅] LangChain loaded.")
    if llama_index:
        ai["llama_index"] = llama_index
        logger.info("[✅] LlamaIndex loaded.")
    if haystack:
        ai["haystack"] = haystack
        logger.info("[✅] Haystack loaded.")
    if litellm:
        ai["litellm"] = litellm
        logger.info("[✅] LiteLLM loaded.")
    if scrapegraph:
        ai["scrapegraph"] = scrapegraph
        logger.info("[✅] ScrapeGraph loaded.")

    return ai


def init_multi_agents():
    """Initialize all multi-agent frameworks."""
    agents = {}

    autogen = try_import("autogen")
    crewai = try_import("crewai")
    langgraph = try_import("langgraph")
    swarm = try_import("openai_swarm")
    metagpt = try_import("metagpt")
    superagi = try_import("superagi")
    taskweaver = try_import("taskweaver")
    atomic_agents = try_import("atomic_agents")
    smolagents = try_import("smolagents")

    frameworks = {
        "autogen": autogen,
        "crewai": crewai,
        "langgraph": langgraph,
        "swarm": swarm,
        "metagpt": metagpt,
        "superagi": superagi,
        "taskweaver": taskweaver,
        "atomic_agents": atomic_agents,
        "smolagents": smolagents,
    }

    for name, module in frameworks.items():
        if module:
            agents[name] = module
            logger.info(f"[✅] {name.capitalize()} initialized.")
        else:
            logger.info(f"[❌] {name.capitalize()} not available.")

    return agents


def init_enterprise():
    """Initialize enterprise and hybrid frameworks."""
    sk = try_import("semantic_kernel")
    rasa = try_import("rasa")

    enterprise = {}
    if sk:
        enterprise["semantic_kernel"] = sk
        logger.info("[✅] Semantic Kernel ready.")
    if rasa:
        enterprise["rasa"] = rasa
        logger.info("[✅] Rasa loaded.")

    return enterprise


def init_transformers():
    """Initialize model and vector libraries."""
    tf = try_import("transformers")
    hf_hub = try_import("huggingface_hub")
    sentence_tf = try_import("sentence_transformers")
    chroma = try_import("chromadb")
    faiss = try_import("faiss")
    weaviate = try_import("weaviate")
    pinecone = try_import("pinecone")
    milvus = try_import("milvus")

    vectors = {}
    modules = {
        "transformers": tf,
        "huggingface_hub": hf_hub,
        "sentence_transformers": sentence_tf,
        "chromadb": chroma,
        "faiss": faiss,
        "weaviate": weaviate,
        "pinecone": pinecone,
        "milvus": milvus,
    }

    for name, module in modules.items():
        if module:
            vectors[name] = module
            logger.info(f"[✅] {name} ready.")
        else:
            logger.info(f"[❌] {name} not found.")

    return vectors


def init_all():
    """Initialize all frameworks and return registry dictionary."""
    logger.info("🔧 Initializing AI frameworks...")

    registry = {
        "core": init_core_ai(),
        "multi_agents": init_multi_agents(),
        "enterprise": init_enterprise(),
        "transformers": init_transformers(),
    }

    total_loaded = sum(len(group) for group in registry.values())
    logger.info(f"✅ Initialization complete. {total_loaded} frameworks ready.")

    return registry


# --- Execute on import ---
AI_REGISTRY = init_all()


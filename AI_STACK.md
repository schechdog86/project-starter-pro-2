# 🤖 AI & Multi-Agent Framework Stack

Complete enterprise-grade AI backend foundation with multi-agent orchestration capabilities.

---

## 📦 Installed Frameworks

### **Core AI & RAG**

| Framework | Purpose | Documentation |
|-----------|---------|---------------|
| **LangChain** | LLM application framework with chains, agents, and memory | [docs](https://python.langchain.com/) |
| **LlamaIndex** | Data framework for LLM applications with advanced RAG | [docs](https://docs.llamaindex.ai/) |
| **Haystack** | End-to-end NLP framework for search and QA | [docs](https://haystack.deepset.ai/) |
| **LiteLLM** | Unified API for 100+ LLMs (OpenAI, Anthropic, etc.) | [docs](https://docs.litellm.ai/) |
| **ScrapeGraph-AI** | AI-powered web scraping with LLMs | [docs](https://scrapegraph-ai.readthedocs.io/) |

### **Multi-Agent Systems**

| Framework | Purpose | Best For |
|-----------|---------|----------|
| **AutoGen** | Microsoft's LLM orchestration with conversational agents | Complex multi-agent conversations |
| **CrewAI** | Role-based multi-agent teamwork | Task delegation and collaboration |
| **LangGraph** | Graph-based stateful multi-agent systems | Complex workflows with state management |
| **OpenAI Swarm** | Lightweight multi-agent coordination | Simple agent handoffs and routing |
| **MetaGPT** | Hierarchical agent collaboration (software company simulation) | Software development workflows |
| **SuperAGI** | Full open-source agent management platform | Production agent deployment |
| **TaskWeaver** | Microsoft agent for workflow and data analytics | Data analysis and code execution |
| **Atomic Agents** | Schema-based modular agent framework | Type-safe agent development |
| **Smolagents** | Lightweight, minimal abstraction agents | Simple agent tasks |

### **Enterprise & Hybrid**

| Framework | Purpose | Use Case |
|-----------|---------|----------|
| **Semantic Kernel** | Microsoft framework for embedding AI "skills" | Enterprise AI integration |
| **Rasa** | Conversational AI / chatbot framework | Customer support bots |

### **Transformer Ecosystem**

| Package | Purpose |
|---------|---------|
| **Transformers** | Hugging Face transformer models |
| **Sentence-Transformers** | Semantic text embeddings |
| **Hugging Face Hub** | Model hosting and API access |
| **Datasets** | Dataset loading and processing |
| **Evaluate** | Model evaluation toolkit |
| **Tiktoken** | OpenAI tokenizer |

### **Vector Databases & Memory**

| Database | Purpose | Best For |
|----------|---------|----------|
| **ChromaDB** | Embedded vector database | Local development, small-scale |
| **Weaviate** | Cloud-native vector search | Production, scalability |
| **Pinecone** | Managed vector database | Serverless, managed service |
| **Milvus** | Open-source vector database | Self-hosted, large-scale |
| **FAISS** | Facebook AI similarity search | Fast similarity search |
| **Redis** | In-memory data store | Caching, session storage |

---

## 🚀 Quick Start Examples

### **1. LangChain - Simple LLM Chain**

```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from backend.app.core.config import settings

# Initialize LLM
llm = OpenAI(api_key=settings.OPENAI_API_KEY)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a brief summary about {topic}"
)

# Create chain
chain = LLMChain(llm=llm, prompt=prompt)

# Run
result = chain.run(topic="artificial intelligence")
print(result)
```

### **2. LlamaIndex - RAG with Documents**

```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms import OpenAI
from backend.app.core.config import settings

# Load documents
documents = SimpleDirectoryReader('data').load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is the main topic?")
print(response)
```

### **3. CrewAI - Multi-Agent Team**

```python
from crewai import Agent, Task, Crew
from backend.app.core.config import settings

# Define agents
researcher = Agent(
    role='Researcher',
    goal='Research and gather information',
    backstory='Expert at finding relevant information',
    verbose=True
)

writer = Agent(
    role='Writer',
    goal='Write engaging content',
    backstory='Skilled content creator',
    verbose=True
)

# Define tasks
research_task = Task(
    description='Research AI trends in 2024',
    agent=researcher
)

write_task = Task(
    description='Write a blog post about AI trends',
    agent=writer
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

# Execute
result = crew.kickoff()
print(result)
```

### **4. LangGraph - Stateful Agent**

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from backend.app.core.config import settings

# Define state
class AgentState(TypedDict):
    messages: list
    next_step: str

# Define nodes
def research_node(state: AgentState):
    # Research logic
    state["messages"].append("Research complete")
    state["next_step"] = "write"
    return state

def write_node(state: AgentState):
    # Writing logic
    state["messages"].append("Writing complete")
    state["next_step"] = END
    return state

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("research", research_node)
workflow.add_node("write", write_node)
workflow.add_edge("research", "write")
workflow.set_entry_point("research")

# Compile and run
app = workflow.compile()
result = app.invoke({"messages": [], "next_step": "research"})
print(result)
```

### **5. LiteLLM - Unified LLM API**

```python
from litellm import completion
from backend.app.core.config import settings

# Works with OpenAI, Anthropic, DeepSeek, etc.
response = completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}],
    api_key=settings.OPENAI_API_KEY
)

# Or use Anthropic
response = completion(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "Hello!"}],
    api_key=settings.ANTHROPIC_API_KEY
)

print(response.choices[0].message.content)
```

### **6. ChromaDB - Vector Storage**

```python
import chromadb
from chromadb.config import Settings

# Initialize client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/data/chromadb"
))

# Create collection
collection = client.create_collection("documents")

# Add documents
collection.add(
    documents=["AI is transforming industries", "Machine learning is powerful"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["artificial intelligence"],
    n_results=2
)
print(results)
```

---

## 🔧 Configuration

### **Environment Variables**

All AI configuration is managed through `.env`:

```bash
# Copy example
cp .env.example .env

# Edit with your API keys
nano .env
```

### **Required API Keys**

| Provider | Get Key | Environment Variable |
|----------|---------|---------------------|
| OpenAI | [platform.openai.com](https://platform.openai.com) | `OPENAI_API_KEY` |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | `ANTHROPIC_API_KEY` |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com) | `DEEPSEEK_API_KEY` |
| Hugging Face | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | `HUGGINGFACE_API_KEY` |

---

## 📊 Framework Comparison

### **When to Use What?**

| Use Case | Recommended Framework |
|----------|----------------------|
| Simple LLM calls | LiteLLM |
| RAG with documents | LlamaIndex |
| Complex chains | LangChain |
| Multi-agent collaboration | CrewAI |
| Stateful workflows | LangGraph |
| Conversational agents | AutoGen |
| Software development agents | MetaGPT |
| Data analysis agents | TaskWeaver |
| Production agent platform | SuperAGI |
| Chatbots | Rasa |

---

## 🐳 Docker Integration

All AI frameworks are pre-installed in Docker images:

```bash
# Build with AI stack
docker compose build

# Run
docker compose up -d

# Verify installation
docker compose exec backend python -c "import langchain; print('LangChain:', langchain.__version__)"
```

---

## 📚 Resources

- **LangChain**: https://python.langchain.com/
- **LlamaIndex**: https://docs.llamaindex.ai/
- **CrewAI**: https://docs.crewai.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **AutoGen**: https://microsoft.github.io/autogen/
- **LiteLLM**: https://docs.litellm.ai/

---

## ✅ Next Steps

1. **Set API Keys** - Add your API keys to `.env`
2. **Choose Framework** - Pick the right tool for your use case
3. **Build Agents** - Create your first AI agent
4. **Test Locally** - Run and iterate
5. **Deploy** - Use Docker for production

---

**Happy AI Building! 🤖🚀**


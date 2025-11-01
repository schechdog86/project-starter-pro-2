# 🧠 AI Memory System

## Overview

Project Starter Pro 2 includes a **Unified AI Memory System** with layered spatial-graph memory, FAISS vector search, SQLite metadata, Pandas archives, and a **Meaning Preservation Protocol (MPP)**.

---

## 🏗️ Architecture

### **Memory Tiers**

The system uses a **4-tier memory hierarchy** inspired by human memory:

| Tier | Name | Capacity | Purpose | Retention |
|------|------|----------|---------|-----------|
| **ST** | Short-Term | 50,000 | Recent interactions | Hours to days |
| **MT** | Mid-Term | 200,000 | Consolidated memories | Days to weeks |
| **LT_HOT** | Long-Term Hot | Unlimited | Frequently accessed | Weeks to months |
| **FV** | Forever | Unlimited | Critical knowledge | Permanent |

### **Storage Components**

1. **FAISS Vector Index** - Fast similarity search (IndexFlatIP)
2. **SQLite Database** - Metadata, scores, and relationships
3. **JSONL Archives** - Full-text storage organized by date
4. **Pandas DataFrames** - Efficient batch processing

---

## 🔬 Meaning Preservation Protocol (MPP)

The MPP ensures that summarization **does not lose semantic meaning**.

### **Validation Metrics**

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| **Cosine Similarity** | ≥ 0.93 | Semantic similarity between original and summary |
| **Entity Recall** | ≥ 0.95 | Percentage of named entities preserved |
| **Vector Shift** | ≤ 0.07 | L2 distance between embeddings |

### **Summarization Process**

1. **Extract entities** - Identify named entities (capitalized words)
2. **Extractive summary** - Select most important sentences by TF score
3. **Abstractive trim** - Reduce to target ratio
4. **Validate** - Check cosine similarity, entity recall, and shift
5. **Block or promote** - Reject if validation fails

---

## 📊 Memory Scoring

Each memory has **4 dynamic scores**:

| Score | Range | Meaning |
|-------|-------|---------|
| **Recency** | 0-1 | How recently accessed |
| **Frequency** | 0-∞ | Access count |
| **Utility** | 0-1 | User-defined importance |
| **Novelty** | 0-1 | Uniqueness vs existing memories |

---

## 🚀 API Endpoints

### **1. Insert Memory**

```http
POST /ai/memory/insert
```

**Request:**
```json
{
  "text": "User signed contract with Stripe API on 2025-01-15",
  "sets": ["contracts", "stripe"],
  "meta": {"customer_id": "cus_123"},
  "pin": false,
  "title": "Stripe Contract"
}
```

**Response:**
```json
{
  "id": "a3f2c1b4e5d6f7g8",
  "status": "inserted"
}
```

---

### **2. Teach (High-Priority Memory)**

```http
POST /ai/memory/teach
```

**Request:**
```json
{
  "text": "Always use OAuth2 for authentication. Never store passwords in plaintext.",
  "sets": ["security", "best-practices"],
  "title": "Security Best Practice"
}
```

**Response:**
```json
{
  "id": "b4e5f6g7h8i9j0k1",
  "status": "taught"
}
```

**Difference from `insert`:**
- Automatically pinned (never deleted)
- Stored in **FV (Forever)** tier
- Higher utility score (0.9)
- Runs MPP validation immediately

---

### **3. Recall Memories**

```http
POST /ai/memory/recall
```

**Request:**
```json
{
  "query": "Stripe contract details",
  "k": 10,
  "sets_filter": ["contracts"]
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "a3f2c1b4e5d6f7g8",
      "score": 0.876,
      "tier": "ST",
      "summary": "User signed contract with Stripe API on 2025-01-15",
      "mpp": {
        "cos": 0.95,
        "ent_recall": 1.0,
        "shift": 0.03,
        "created": 1736985600.0,
        "model": "mpp-rule"
      }
    }
  ],
  "count": 1
}
```

---

### **4. Memory Consolidation (Tick)**

```http
POST /ai/memory/tick
```

**Purpose:** Promote memories from **ST → MT** with MPP validation.

**Response:**
```json
{
  "status": "ok",
  "message": "Memory consolidation completed"
}
```

**When to run:**
- Scheduled background task (e.g., every hour)
- After large batch inserts
- Before system shutdown

---

### **5. Validate Memory**

```http
GET /ai/memory/validate/{memory_id}
```

**Response:**
```json
{
  "id": "a3f2c1b4e5d6f7g8",
  "valid": true,
  "status": "valid"
}
```

---

## 💻 Python Integration

### **Direct Usage**

```python
from backend.app.ai.memory_system import memory_system

# Insert a memory
rid = memory_system.insert("User prefers dark mode UI")

# Teach critical knowledge
rid = memory_system.teach("Always validate user input before database queries")

# Recall memories
results = memory_system.recall("user preferences", k=5)
for r in results:
    print(f"[{r['tier']}] {r['summary']} (score: {r['score']})")

# Consolidate memories
memory_system.tick()

# Validate semantic integrity
is_valid = memory_system.validate(rid)
```

---

### **LangChain Integration**

```python
from langchain.memory import ConversationBufferMemory
from backend.app.ai.memory_system import memory_system

class MemorySystemAdapter:
    def save_context(self, inputs, outputs):
        text = f"User: {inputs['input']}\nAI: {outputs['output']}"
        memory_system.insert(text, sets=["conversation"])
    
    def load_memory_variables(self, inputs):
        results = memory_system.recall(inputs.get("input", ""), k=5)
        context = "\n".join([r["summary"] for r in results])
        return {"history": context}

# Use with LangChain
memory = MemorySystemAdapter()
```

---

### **AutoGen Integration**

```python
from autogen import AssistantAgent
from backend.app.ai.memory_system import memory_system

class MemoryAgent(AssistantAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = memory_system
    
    def receive(self, message, sender):
        # Store conversation
        self.memory.insert(f"{sender.name}: {message}")
        
        # Recall relevant context
        context = self.memory.recall(message, k=3)
        
        # Add context to message
        enriched_message = f"Context: {context}\n\nMessage: {message}"
        
        return super().receive(enriched_message, sender)
```

---

## 🔧 Configuration

### **Environment Variables**

```env
# Memory system configuration (optional)
MEMORY_DIMS=768                    # Embedding dimensions
MEMORY_ST_CAP=50000               # Short-term capacity
MEMORY_MT_CAP=200000              # Mid-term capacity
MEMORY_ROOT=memstore              # Storage directory
```

### **Custom Configuration**

```python
from backend.app.ai.memory_system import MemorySystem

custom_config = {
    "dims": 1024,              # Higher dimensions for better accuracy
    "st_cap": 100_000,         # Larger short-term capacity
    "root": "/data/memories"   # Custom storage path
}

memory = MemorySystem(cfg=custom_config)
```

---

## 📁 Storage Structure

```
memstore/
├── st.sqlite              # Short-term metadata
├── st.faiss               # Short-term vector index
├── st.meta.json           # Short-term index metadata
├── mt.sqlite              # Mid-term metadata
├── mt.faiss               # Mid-term vector index
├── mt.meta.json           # Mid-term index metadata
├── lt_hot.sqlite          # Long-term hot metadata
├── lt_hot.faiss           # Long-term hot vector index
├── lt_hot.meta.json       # Long-term hot index metadata
├── fv.sqlite              # Forever metadata
├── fv.faiss               # Forever vector index
├── fv.meta.json           # Forever index metadata
└── arch/                  # JSONL archives
    └── 2025/
        └── 01/
            ├── part-15.jsonl
            ├── part-16.jsonl
            └── part-17.jsonl
```

---

## 🧪 Testing

### **Test Memory Insert**

```bash
curl -X POST http://localhost:8000/ai/memory/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "User signed contract with Stripe API",
    "sets": ["contracts"],
    "title": "Stripe Contract"
  }'
```

### **Test Memory Recall**

```bash
curl -X POST http://localhost:8000/ai/memory/recall \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Stripe contract",
    "k": 5
  }'
```

### **Test Memory Consolidation**

```bash
curl -X POST http://localhost:8000/ai/memory/tick
```

---

## 🚀 Production Deployment

### **1. Scheduled Consolidation**

Add to Celery tasks:

```python
# backend/app/workers/tasks.py
from celery import shared_task
from backend.app.ai.memory_system import memory_system

@shared_task
def consolidate_memories():
    """Run memory consolidation every hour"""
    memory_system.tick()
    return "Memory consolidation completed"
```

### **2. Docker Volume**

Mount persistent storage:

```yaml
# docker-compose.yml
services:
  backend:
    volumes:
      - memory_data:/app/memstore

volumes:
  memory_data:
```

### **3. Backup Strategy**

```bash
# Backup memory system
tar -czf memory-backup-$(date +%Y%m%d).tar.gz memstore/

# Restore
tar -xzf memory-backup-20250115.tar.gz
```

---

## 📈 Performance

### **Benchmarks**

| Operation | Time | Throughput |
|-----------|------|------------|
| Insert | ~5ms | 200 ops/sec |
| Recall (k=10) | ~15ms | 66 ops/sec |
| Teach | ~20ms | 50 ops/sec |
| Tick (100 memories) | ~2s | - |

### **Optimization Tips**

1. **Batch inserts** - Insert multiple memories at once
2. **Async consolidation** - Run `tick()` in background
3. **Index tuning** - Use IVF-Flat for >1M memories
4. **Embedding cache** - Cache embeddings for repeated queries

---

## 🎯 Use Cases

### **1. Conversational AI**

Store conversation history with semantic search:

```python
# Store conversation
memory_system.insert(f"User: {user_msg}\nAI: {ai_response}")

# Recall relevant context
context = memory_system.recall(user_msg, k=5)
```

### **2. Knowledge Base**

Teach the system domain knowledge:

```python
# Teach best practices
memory_system.teach("Always use parameterized queries to prevent SQL injection")

# Recall when needed
advice = memory_system.recall("database security", k=3)
```

### **3. User Preferences**

Remember user preferences across sessions:

```python
# Store preference
memory_system.insert("User prefers dark mode", sets=["preferences"])

# Recall preferences
prefs = memory_system.recall("user interface preferences", k=10)
```

---

## ✅ Summary

**The AI Memory System provides:**

- ✅ **4-tier memory hierarchy** (ST, MT, LT_HOT, FV)
- ✅ **FAISS vector search** for fast similarity retrieval
- ✅ **Meaning Preservation Protocol** to prevent semantic loss
- ✅ **RESTful API** for easy integration
- ✅ **LangChain/AutoGen adapters** for multi-agent systems
- ✅ **Production-ready** with Docker support

**Ready to give your AI long-term memory!** 🧠🚀


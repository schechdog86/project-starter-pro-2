# Embedding Provider Configuration

The Vector DB Manager supports multiple embedding providers for flexible deployment options. Configure the provider using environment variables.

## Environment Variables

### Core Configuration
- **PSP_EMBED_PROVIDER**: Provider name (default: `voyageai`)
- **PSP_EMBED_MODEL**: Model name (uses provider's default if not specified)
- **PSP_VDB_CREATE_GLOBAL**: Set to `0` to disable global instance creation (useful for testing)

### Provider-Specific API Keys
- **VOYAGE_API_KEY**: Required for VoyageAI provider
- **OPENAI_API_KEY**: Required for OpenAI provider
- **OLLAMA_BASE_URL**: Ollama server URL (default: `http://localhost:11434`)

## Supported Providers

### 1. VoyageAI (Default)
High-quality embeddings with specialized models for different domains.

**Models:**
- `voyage-3` (1024 dims) - General-purpose, recommended for most use cases
- `voyage-3-lite` (512 dims) - Lighter, faster version
- `voyage-code-2` (1536 dims) - Optimized for code with 16K context
- `voyage-finance-2` (1024 dims) - Financial domain
- `voyage-law-2` (1024 dims) - Legal domain

**Configuration:**
```bash
export PSP_EMBED_PROVIDER="voyageai"
export PSP_EMBED_MODEL="voyage-3"
export VOYAGE_API_KEY="your-api-key"
```

**Pros:**
- Excellent retrieval quality, especially for code
- Specialized domain models available
- Native LanceDB integration

**Cons:**
- Requires API key and billing
- Rate limits on free tier
- External API dependency

---

### 2. OpenAI
Industry-standard embeddings with proven performance.

**Models:**
- `text-embedding-3-small` (1536 dims) - Cost-effective, good quality
- `text-embedding-3-large` (3072 dims) - Highest quality
- `text-embedding-ada-002` (1536 dims) - Legacy model

**Configuration:**
```bash
export PSP_EMBED_PROVIDER="openai"
export PSP_EMBED_MODEL="text-embedding-3-small"
export OPENAI_API_KEY="your-api-key"
```

**Pros:**
- Proven quality and reliability
- Wide adoption and documentation
- Native LanceDB integration

**Cons:**
- Requires API key and billing
- Higher cost than some alternatives
- External API dependency

---

### 3. Ollama (Local or Cloud)
Run models locally or use Ollama Cloud for privacy and cost control.

**Models:**
- `nomic-embed-text` (768 dims) - Excellent open-source model
- `mxbai-embed-large` (1024 dims) - High-quality embeddings
- `bge-m3` (1024 dims) - Multilingual support
- `all-minilm` (384 dims) - Fast and lightweight

**Configuration (Local):**
```bash
# Start Ollama server first: ollama serve
# Pull model: ollama pull nomic-embed-text

export PSP_EMBED_PROVIDER="ollama"
export PSP_EMBED_MODEL="nomic-embed-text"
export OLLAMA_BASE_URL="http://localhost:11434"  # Optional, this is default
```

**Configuration (Cloud):**
```bash
export PSP_EMBED_PROVIDER="ollama"
export PSP_EMBED_MODEL="nomic-embed-text"
export OLLAMA_BASE_URL="https://your-ollama-cloud-url"
```

**Pros:**
- No API costs for local deployment
- Complete privacy (local mode)
- No rate limits
- Good quality open-source models

**Cons:**
- Requires local resources (CPU/GPU, memory)
- Slightly lower quality than top commercial models
- Need to manage Ollama installation

---

### 4. Sentence Transformers
Direct integration with Hugging Face sentence-transformers models.

**Models:**
- `all-MiniLM-L6-v2` (384 dims) - Fast and lightweight
- `all-mpnet-base-v2` (768 dims) - Better quality

**Configuration:**
```bash
export PSP_EMBED_PROVIDER="sentence-transformers"
export PSP_EMBED_MODEL="all-MiniLM-L6-v2"
```

**Pros:**
- Completely local, no API needed
- Free and open-source
- Fast inference

**Cons:**
- Lower quality than specialized models
- Requires model download on first use
- Limited to available sentence-transformers models

---

## Quick Start Examples

### Development (Local Ollama)
```bash
# Install and start Ollama
ollama serve
ollama pull nomic-embed-text

# Configure environment
export PSP_EMBED_PROVIDER="ollama"
export PSP_EMBED_MODEL="nomic-embed-text"

# Run your application
python backend/app/main.py
```

### Production (VoyageAI)
```bash
# Configure environment
export PSP_EMBED_PROVIDER="voyageai"
export PSP_EMBED_MODEL="voyage-3"
export VOYAGE_API_KEY="pa-your-api-key"

# Run your application
python backend/app/main.py
```

### Testing (Lightweight Local)
```bash
# Use fast, small model for tests
export PSP_EMBED_PROVIDER="sentence-transformers"
export PSP_EMBED_MODEL="all-MiniLM-L6-v2"
export PSP_VDB_CREATE_GLOBAL="0"  # Disable global instance

# Run tests
pytest backend/tests/
```

---

## Switching Providers

When you switch providers or models with different dimensions, the vector database table will be automatically recreated with the correct schema. **This will clear existing data**, so:

1. **Backup important data** before switching
2. **Re-index your codebase** after switching
3. Consider using separate database paths for different providers:

```bash
# Use provider-specific paths
export PSP_VDB_PATH="/data/vector_db_voyage"  # For VoyageAI
export PSP_VDB_PATH="/data/vector_db_ollama"  # For Ollama
```

---

## Performance Comparison

| Provider | Model | Dims | Speed | Quality | Cost | Privacy |
|----------|-------|------|-------|---------|------|---------|
| VoyageAI | voyage-3 | 1024 | Fast | Excellent | $$ | Cloud |
| VoyageAI | voyage-code-2 | 1536 | Fast | Excellent (code) | $$ | Cloud |
| OpenAI | text-embedding-3-small | 1536 | Fast | Very Good | $ | Cloud |
| Ollama | nomic-embed-text | 768 | Medium | Good | Free | Local |
| Ollama | mxbai-embed-large | 1024 | Medium | Very Good | Free | Local |
| Sentence-Transformers | all-mpnet-base-v2 | 768 | Fast | Good | Free | Local |

---

## Troubleshooting

### "API key not found" Error
Make sure the appropriate API key environment variable is set:
```bash
# For VoyageAI
export VOYAGE_API_KEY="your-key"

# For OpenAI
export OPENAI_API_KEY="your-key"
```

### "Unsupported embedding provider" Error
Check that PSP_EMBED_PROVIDER is set to a valid provider name:
- `voyageai`
- `openai`
- `ollama`
- `sentence-transformers`

### Ollama Connection Error
Ensure Ollama is running:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### Model Not Found (Ollama)
Pull the model first:
```bash
ollama pull nomic-embed-text
```

### Dimension Mismatch
If you see dimension errors, the table schema doesn't match your current model. Clear the table:
```python
from backend.app.ai.vector_db_manager import vector_db_manager
vector_db_manager.clear_table()
```

---

## Adding New Providers

To add a new provider, edit `backend/app/ai/vector_db_manager.py`:

1. Add provider configuration to `PROVIDER_CONFIG` dictionary
2. Add initialization logic in `_initialize_embedding_function()`
3. Update this documentation

Example:
```python
PROVIDER_CONFIG = {
    # ... existing providers ...
    "cohere": {
        "models": {
            "embed-english-v3.0": {"dims": 1024, "api_key_env": "COHERE_API_KEY"},
        },
        "default_model": "embed-english-v3.0",
    },
}
```


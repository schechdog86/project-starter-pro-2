"""
Examples of using different embedding providers with the Vector DB Manager.

This file demonstrates how to easily switch between providers using environment variables.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def example_voyageai():
    """Example: Using VoyageAI (default provider)"""
    print("\n" + "="*60)
    print("Example 1: VoyageAI Provider (Default)")
    print("="*60)
    
    # Configure VoyageAI
    os.environ["PSP_EMBED_PROVIDER"] = "voyageai"
    os.environ["PSP_EMBED_MODEL"] = "voyage-3"
    os.environ["VOYAGE_API_KEY"] = "your-voyage-api-key"
    os.environ["PSP_VDB_CREATE_GLOBAL"] = "0"  # Disable global instance
    
    from app.ai.vector_db_manager import VectorDBManager
    
    # Create manager
    vdb = VectorDBManager(db_path="./temp_db_voyage")
    
    print(f"✓ Provider: {vdb.provider}")
    print(f"✓ Model: {vdb.model}")
    print(f"✓ Vector Dimension: {vdb.vector_dim}")
    
    # Add some code chunks
    chunks = [
        {
            "filename": "auth.py",
            "text": "def authenticate_user(username, password): verify credentials and return token",
            "chunk_index": 0,
            "total_chunks": 1,
        },
        {
            "filename": "database.py",
            "text": "class DatabaseConnection: manage database connections with connection pooling",
            "chunk_index": 0,
            "total_chunks": 1,
        },
    ]
    
    vdb.add_chunks(chunks)
    print(f"✓ Added {len(chunks)} chunks")
    
    # Search
    results = vdb.search("How do I authenticate users?", limit=2)
    print(f"✓ Search returned {len(results)} results")
    if results:
        print(f"  Top result: {results[0]['filename']}")


def example_ollama_local():
    """Example: Using Ollama with local model"""
    print("\n" + "="*60)
    print("Example 2: Ollama Provider (Local)")
    print("="*60)
    
    # Configure Ollama
    os.environ["PSP_EMBED_PROVIDER"] = "ollama"
    os.environ["PSP_EMBED_MODEL"] = "nomic-embed-text"
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["PSP_VDB_CREATE_GLOBAL"] = "0"
    
    from app.ai.vector_db_manager import VectorDBManager
    
    # Create manager
    vdb = VectorDBManager(db_path="./temp_db_ollama")
    
    print(f"✓ Provider: {vdb.provider}")
    print(f"✓ Model: {vdb.model}")
    print(f"✓ Vector Dimension: {vdb.vector_dim}")
    print(f"✓ No API key required - running locally!")
    
    # Add chunks
    chunks = [
        {
            "filename": "api.py",
            "text": "FastAPI endpoint for user registration with email validation",
            "chunk_index": 0,
            "total_chunks": 1,
        },
    ]
    
    vdb.add_chunks(chunks)
    print(f"✓ Added {len(chunks)} chunks")


def example_openai():
    """Example: Using OpenAI embeddings"""
    print("\n" + "="*60)
    print("Example 3: OpenAI Provider")
    print("="*60)
    
    # Configure OpenAI
    os.environ["PSP_EMBED_PROVIDER"] = "openai"
    os.environ["PSP_EMBED_MODEL"] = "text-embedding-3-small"
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    os.environ["PSP_VDB_CREATE_GLOBAL"] = "0"
    
    from app.ai.vector_db_manager import VectorDBManager
    
    # Create manager
    vdb = VectorDBManager(db_path="./temp_db_openai")
    
    print(f"✓ Provider: {vdb.provider}")
    print(f"✓ Model: {vdb.model}")
    print(f"✓ Vector Dimension: {vdb.vector_dim}")


def example_sentence_transformers():
    """Example: Using Sentence Transformers (completely local)"""
    print("\n" + "="*60)
    print("Example 4: Sentence Transformers (Fully Local)")
    print("="*60)
    
    # Configure Sentence Transformers
    os.environ["PSP_EMBED_PROVIDER"] = "sentence-transformers"
    os.environ["PSP_EMBED_MODEL"] = "all-MiniLM-L6-v2"
    os.environ["PSP_VDB_CREATE_GLOBAL"] = "0"
    
    from app.ai.vector_db_manager import VectorDBManager
    
    # Create manager
    vdb = VectorDBManager(db_path="./temp_db_st")
    
    print(f"✓ Provider: {vdb.provider}")
    print(f"✓ Model: {vdb.model}")
    print(f"✓ Vector Dimension: {vdb.vector_dim}")
    print(f"✓ Completely local - no API, no network calls!")


def example_switching_providers():
    """Example: Switching between providers dynamically"""
    print("\n" + "="*60)
    print("Example 5: Dynamic Provider Switching")
    print("="*60)
    
    providers = [
        ("voyageai", "voyage-3", 1024),
        ("openai", "text-embedding-3-small", 1536),
        ("ollama", "nomic-embed-text", 768),
        ("sentence-transformers", "all-MiniLM-L6-v2", 384),
    ]
    
    for provider, model, expected_dim in providers:
        os.environ["PSP_EMBED_PROVIDER"] = provider
        os.environ["PSP_EMBED_MODEL"] = model
        os.environ["PSP_VDB_CREATE_GLOBAL"] = "0"
        
        # Need to reload module to pick up new env vars
        import importlib
        if "app.ai.vector_db_manager" in sys.modules:
            importlib.reload(sys.modules["app.ai.vector_db_manager"])
        
        from app.ai.vector_db_manager import VectorDBManager
        
        vdb = VectorDBManager(db_path=f"./temp_db_{provider}")
        
        print(f"\n{provider}:")
        print(f"  Model: {vdb.model}")
        print(f"  Dimensions: {vdb.vector_dim} (expected: {expected_dim})")
        print(f"  ✓ Schema created successfully")


def example_production_config():
    """Example: Production configuration with environment-based selection"""
    print("\n" + "="*60)
    print("Example 6: Production Configuration Pattern")
    print("="*60)
    
    # Simulate different environments
    environments = {
        "development": {
            "PSP_EMBED_PROVIDER": "ollama",
            "PSP_EMBED_MODEL": "nomic-embed-text",
            "OLLAMA_BASE_URL": "http://localhost:11434",
        },
        "staging": {
            "PSP_EMBED_PROVIDER": "voyageai",
            "PSP_EMBED_MODEL": "voyage-3-lite",  # Cheaper for staging
            "VOYAGE_API_KEY": "staging-api-key",
        },
        "production": {
            "PSP_EMBED_PROVIDER": "voyageai",
            "PSP_EMBED_MODEL": "voyage-3",  # Best quality for prod
            "VOYAGE_API_KEY": "production-api-key",
        },
    }
    
    for env_name, env_vars in environments.items():
        print(f"\n{env_name.upper()} Environment:")
        for key, value in env_vars.items():
            if "KEY" in key:
                value = "***" + value[-8:]  # Mask API keys
            print(f"  {key}={value}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Vector DB Manager - Multi-Provider Examples")
    print("="*60)
    print("\nThese examples show how to use different embedding providers.")
    print("Uncomment the examples you want to run.\n")
    
    # Uncomment to run specific examples:
    
    # example_voyageai()
    # example_ollama_local()
    # example_openai()
    # example_sentence_transformers()
    # example_switching_providers()
    example_production_config()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nTo use in your code:")
    print("1. Set environment variables (PSP_EMBED_PROVIDER, PSP_EMBED_MODEL)")
    print("2. Set provider-specific API keys if needed")
    print("3. Import and use VectorDBManager")
    print("\nSee backend/docs/EMBEDDING_PROVIDERS.md for full documentation.")


if __name__ == "__main__":
    main()


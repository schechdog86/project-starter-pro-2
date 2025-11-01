from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Starter Pro 2"

    # === DATABASE CONFIGURATION ===
    POSTGRES_URL: str = Field(
        default="postgresql+asyncpg://psp_user:psp_pass@localhost:5432/psp",
        description="PostgreSQL database URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    # === JWT / SECURITY ===
    SECRET_KEY: str = Field(
        default="replace_this_key",
        description="JWT secret key"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        description="JWT token expiration in minutes"
    )

    # === AI API KEYS ===
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key"
    )
    ANTHROPIC_API_KEY: str = Field(
        default="",
        description="Anthropic Claude API key"
    )
    DEEPSEEK_API_KEY: str = Field(
        default="",
        description="DeepSeek API key"
    )
    HUGGINGFACE_API_KEY: str = Field(
        default="",
        description="Hugging Face API key"
    )

    # === MODEL CONFIGURATION ===
    MODEL_PROVIDER: str = Field(
        default="openai",
        description="Default LLM provider (openai, anthropic, deepseek)"
    )
    MODEL_PATH: str = Field(
        default="/models",
        description="Path to store downloaded models"
    )
    EMBEDDING_BACKEND: str = Field(
        default="sentence-transformers",
        description="Embedding model backend"
    )
    VECTOR_DB: str = Field(
        default="chromadb",
        description="Vector database backend (chromadb, weaviate, pinecone, milvus)"
    )

    # === MULTI-AGENT FRAMEWORKS ===
    AUTOGEN_API_KEY: str = Field(
        default="",
        description="AutoGen API key (defaults to OPENAI_API_KEY)"
    )
    CREWAI_LOG_LEVEL: str = Field(
        default="info",
        description="CrewAI logging level"
    )
    LANGGRAPH_STATE_PATH: str = Field(
        default="/data/langgraph_state",
        description="LangGraph state persistence path"
    )
    SWARM_API_KEY: str = Field(
        default="",
        description="OpenAI Swarm API key (defaults to OPENAI_API_KEY)"
    )
    SUPERAGI_CONFIG_PATH: str = Field(
        default="/app/superagi/config",
        description="SuperAGI configuration path"
    )
    TASKWEAVER_DATA_PATH: str = Field(
        default="/app/taskweaver/data",
        description="TaskWeaver data path"
    )

    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


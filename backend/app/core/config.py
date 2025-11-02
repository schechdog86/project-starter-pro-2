from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Starter Pro 2"

    # === DATABASE CONFIGURATION ===
    DB_TYPE: str = Field(
        default="sqlite",
        description="Database type: 'sqlite' or 'postgres'"
    )
    DB_USER: str = Field(
        default="psp_user",
        description="PostgreSQL username"
    )
    DB_PASS: str = Field(
        default="psp_pass",
        description="PostgreSQL password"
    )
    DB_HOST: str = Field(
        default="localhost",
        description="PostgreSQL host"
    )
    DB_PORT: str = Field(
        default="5432",
        description="PostgreSQL port"
    )
    DB_NAME: str = Field(
        default="psp",
        description="PostgreSQL database name"
    )

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """Get database URL based on DB_TYPE."""
        if self.DB_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://{self.DB_USER}:"
                f"{self.DB_PASS}@{self.DB_HOST}:"
                f"{self.DB_PORT}/{self.DB_NAME}"
            )
        else:
            # SQLite fallback for development
            db_path = Path("data/dev.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_path}"

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
    CLAUDE_API_KEY: str = Field(
        default="",
        description="Claude API key (alias for ANTHROPIC_API_KEY)"
    )
    DEEPSEEK_API_KEY: str = Field(
        default="",
        description="DeepSeek API key"
    )
    HUGGINGFACE_API_KEY: str = Field(
        default="",
        description="Hugging Face API key"
    )
    FIRECRAWL_API_KEY: str = Field(
        default="",
        description="Firecrawl API key"
    )
    SCRAPEGRAPH_API_KEY: str = Field(
        default="",
        description="ScrapeGraph AI API key"
    )
    GITHUB_TOKEN: str = Field(
        default="",
        description="GitHub personal access token"
    )

    # === MODEL CONFIGURATION ===
    MODEL_PROVIDER: str = Field(
        default="openai",
        description="Default LLM provider (openai, anthropic, deepseek)"
    )
    PRIMARY_LLM_MODEL: str = Field(
        default="gpt-4",
        description="Primary LLM model"
    )
    FALLBACK_LLM_MODEL: str = Field(
        default="gpt-3.5-turbo",
        description="Fallback LLM model"
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

    # === API CONFIGURATION ===
    OPENAI_API_BASE: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL"
    )
    CLAUDE_API_BASE: str = Field(
        default="https://api.anthropic.com",
        description="Claude API base URL"
    )
    DEEPSEEK_API_BASE: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API base URL"
    )
    API_TIMEOUT: int = Field(
        default=30,
        description="API request timeout in seconds"
    )
    API_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum API retry attempts"
    )
    API_RETRY_DELAY: int = Field(
        default=1,
        description="Delay between retries in seconds"
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
        extra = "allow"  # Allow extra fields from .env

settings = Settings()


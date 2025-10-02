from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Pipedream
    PIPEDREAM_PROJECT_ID: str
    PIPEDREAM_CLIENT_ID: str
    PIPEDREAM_CLIENT_SECRET: str

    # FalkorDB
    FALKORDB_HOST: str = "localhost"
    FALKORDB_PORT: int = 6379
    FALKORDB_USERNAME: str = ""
    FALKORDB_PASSWORD: str = ""
    FALKORDB_DATABASE: str = "my_app_graph"

    # OpenAI
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

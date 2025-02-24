from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Generation Assistant"
    
    # API Keys
    OPENAI_API_KEY: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_ENDPOINT: str
    LANGCHAIN_PROJECT: str
    LANGCHAIN_TRACING_V2: str
    TAVILY_API_KEY: str
    
    class Config:
        env_file = ".env"

ettings = Settings()
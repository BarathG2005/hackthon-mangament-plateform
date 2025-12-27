from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    Uses pydantic-settings for type validation and .env file support
    """
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    # Application Configuration
    APP_NAME: str = "College Hackathon Management Platform"
    DEBUG: bool = True
    API_VERSION: str = "1.0.0"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    def validate_supabase_config(self) -> None:
        """Validate that Supabase configuration is complete"""
        if not self.SUPABASE_URL or not self.SUPABASE_ANON_KEY:
            raise ValueError(
                "Missing Supabase configuration. "
                "Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file"
            )


# Create a global settings instance
settings = Settings()

# Validate configuration on startup
settings.validate_supabase_config()

"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Atlassian credentials (required)
    atlassian_cloud_id: str
    atlassian_email: str
    atlassian_api_token: str

    # Optional settings
    jira_default_project: str = "PH"
    mcp_log_level: str = "INFO"

    @property
    def jira_base_url(self) -> str:
        """Get Jira base URL."""
        return f"https://{self.atlassian_cloud_id}/rest/api/3"

    @property
    def confluence_base_url(self) -> str:
        """Get Confluence base URL."""
        return f"https://{self.atlassian_cloud_id}/wiki/rest/api"

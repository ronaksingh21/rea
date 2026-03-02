from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gmail_credentials_path: str = "credentials.json"
    gmail_token_path: str = "token.json"
    gmail_query: str = 'subject:("offering memorandum" OR "OM") has:attachment filename:pdf'
    gmail_poll_minutes: int = 5

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    ocr_enabled: bool = True

    slack_bot_token: str = ""
    slack_channel: str = "#deal-intake"

    data_dir: str = "./data"
    database_url: str = "sqlite:///./data/deals.db"


settings = Settings()

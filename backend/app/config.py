from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    waqi_api_token: str = ""
    openaq_api_key: str = ""
    openmeteo_base_url: str = "https://api.open-meteo.com/v1"
    database_url: str = "sqlite:///./saans.db"
    admin_recompute_secret: str = "change-me-before-deploy"
    whatsapp_cloud_api_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "change-me-before-deploy"
    whatsapp_app_secret: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    frontend_base_url: str = "http://localhost:5173"
    backend_base_url: str = "http://localhost:8000"
    bulletin_storage_dir: str = "./bulletins"

    @property
    def waqi_configured(self) -> bool:
        return bool(self.waqi_api_token)

    @property
    def openaq_configured(self) -> bool:
        return bool(self.openaq_api_key)

    @property
    def whatsapp_configured(self) -> bool:
        return bool(self.whatsapp_cloud_api_token and self.whatsapp_phone_number_id)


@lru_cache
def get_settings() -> Settings:
    return Settings()

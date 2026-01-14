from pydantic_settings import BaseSettings, SettingsConfigDict
import json
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "edDSA API Implementation"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Krusial untuk verifikasi EdDSA
    MOCK_PUBLIC_KEYS: str

    # Timeout setting
    REQUEST_TIMEOUT: int = 30

    @property
    def public_keys_map(self) -> dict:
        try:
            clean_json = self.MOCK_PUBLIC_KEYS.strip().strip("'").strip('"')
            return json.loads(clean_json)
        except Exception:
            return {}

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

SETTINGS = Settings()

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    gemini_api_key: str = ""

    hf_api_key: str = ""

    gemini_model: str = "gemini-2.5-flash"

    hf_image_model: str = (
    "stabilityai/stable-diffusion-3-medium-diffusers"
)

    demo_mode: bool = False

    panels: int = 5

    image_width: int = 768

    image_height: int = 768

    max_prompt_length: int = 2000

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
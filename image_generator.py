from pathlib import Path
from uuid import uuid4

from PIL import Image
from huggingface_hub import InferenceClient

from app.config import settings


BASE_DIR = Path(__file__).resolve().parent.parent
PANELS_DIR = BASE_DIR / "static" / "panels"

PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _save_image(
    image: Image.Image,
    panel_number: int,
) -> str:
    filename = (
        f"panel_{panel_number}_"
        f"{uuid4().hex[:8]}.png"
    )

    path = PANELS_DIR / filename

    image.convert("RGB").save(
        path,
        format="PNG",
    )

    if not path.exists():
        raise RuntimeError(
            f"Image was not saved: {path}"
        )

    print(f"Image saved: {path}")

    return f"/static/panels/{filename}"


def _placeholder(
    panel_number: int,
    prompt: str,
) -> str:
    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height,
        ),
        "white",
    )

    return _save_image(
        image,
        panel_number,
    )


def generate_image(
        
    prompt: str,
    panel_number: int,
) -> str:
    if not prompt or not prompt.strip():
        raise ValueError(
            "Image prompt cannot be empty."
        )

    if settings.demo_mode:
        return _placeholder(
            panel_number,
            prompt,
        )

    if not settings.hf_api_key:
        raise RuntimeError(
            "HF_API_KEY is missing. "
            "Add it to .env or enable DEMO_MODE=true."
        )

    client = InferenceClient(
        provider="hf-inference",
        api_key=settings.hf_api_key,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
    )

    if not isinstance(image, Image.Image):
        raise RuntimeError(
            "Hugging Face did not return a valid image."
        )

    return _save_image(
        image,
        panel_number,
    )
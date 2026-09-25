import json

from app.config import settings


try:
    from google import genai
except ImportError:
    genai = None


def _demo_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    panels = []

    for i in range(1, settings.panels + 1):

        panels.append(
            {
                "panel_number": i,

                "title": f"Panel {i}",

                "scene_description": (
                    f"{character_name} faces the next moment "
                    f"of the adventure in {setting}."
                ),

                "image_prompt": (
                    f"{art_style} comic illustration, "
                    f"{character_name}, {setting}, "
                    f"{story_prompt}, panel {i}, "
                    f"expressive characters, cinematic "
                    f"composition, clean line art, "
                    f"detailed background"
                ),
            }
        )

    return panels


def generate_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):

    if settings.demo_mode:

        return _demo_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to .env or enable DEMO_MODE=true."
        )

    if genai is None:

        raise RuntimeError(
            "google-genai is not installed. "
            "Run: pip install -r requirements.txt"
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    prompt = f"""
Create exactly {settings.panels} panels for a comic.

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY valid JSON.

Use this exact structure:

{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "short title",
      "scene_description": "visual scene description",
      "image_prompt": "detailed image-generation prompt"
    }}
  ]
}}

Rules:

- Exactly {settings.panels} panels.
- Keep the main character visually consistent.
- Make the story flow from panel to panel.
- Make the scenes visually interesting.
- Do not use markdown.
- Do not add explanations outside JSON.
"""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    data = json.loads(response.text)

    panels = data.get("panels", [])

    if len(panels) != settings.panels:

        raise RuntimeError(
            f"Gemini returned {len(panels)} panels "
            f"instead of {settings.panels}."
        )

    return panels
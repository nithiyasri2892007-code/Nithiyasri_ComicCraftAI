import json

from app.config import settings


try:
    from google import genai
except ImportError:
    genai = None


def _demo_story(
    outline,
    character_name,
    tone
):

    result = []

    for panel in outline:

        result.append(
            {
                "panel_number": panel["panel_number"],

                "caption": (
                    f"{panel['title']} — "
                    f"the adventure continues."
                ),

                "narration": (
                    f"{character_name} takes a brave step "
                    f"forward. The {tone} moment changes "
                    f"everything."
                ),

                "dialogue": (
                    f'{character_name}: '
                    f'"I have to keep going!"'
                ),
            }
        )

    return result


def generate_story(
    outline,
    character_name,
    tone
):

    if settings.demo_mode:

        return _demo_story(
            outline,
            character_name,
            tone
        )

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    if genai is None:

        raise RuntimeError(
            "google-genai is not installed."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    outline_json = json.dumps(
        outline,
        ensure_ascii=False
    )

    prompt = f"""
Expand the following comic outline into
narration, captions and character dialogue.

Main character:
{character_name}

Tone:
{tone}

Comic outline:

{outline_json}

Return ONLY valid JSON.

Use this structure:

{{
  "panels": [
    {{
      "panel_number": 1,
      "caption": "short caption",
      "narration": "2-3 sentences",
      "dialogue": "one or two short lines"
    }}
  ]
}}

Rules:

- Keep exactly the same panel numbers.
- Preserve story continuity.
- Keep dialogue natural.
- Keep narration suitable for a comic.
- Do not use markdown.
"""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    data = json.loads(response.text)

    return data.get("panels", [])
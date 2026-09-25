from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import JSONResponse

from app.config import settings
from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.schemas import PromptRequest


router = APIRouter()
routes = router


def _validate_text(
    value: str,
    name: str,
) -> str:
    value = value.strip()

    if not value:
        raise HTTPException(
            status_code=400,
            detail=f"{name} is required.",
        )

    if len(value) > settings.max_prompt_length:
        raise HTTPException(
            status_code=400,
            detail=f"{name} is too long.",
        )

    return value


def _generate_comic(
    data: PromptRequest,
) -> dict:
    # Step 1: Generate panel outline
    outline = generate_outline(
        data.story_prompt,
        data.character_name,
        data.setting,
        data.tone,
        data.art_style,
    )

    # Step 2: Generate narration and dialogue
    story = generate_story(
        outline,
        data.character_name,
        data.tone,
    )

    # Step 3: Generate and save images
    image_paths = {}

    for panel in outline:
        panel_number = panel["panel_number"]
        image_prompt = panel["image_prompt"]

        image_paths[panel_number] = generate_image(
            image_prompt,
            panel_number,
        )

    # Step 4: Build comic layout
    layout = build_comic_layout(
        outline,
        story,
        image_paths,
    )

    # Attach the generated image URL to each layout panel.
    for panel in layout:
        panel_number = panel.get("panel_number")

        if panel_number in image_paths:
            panel["image_path"] = image_paths[
                panel_number
            ]

    # Step 5: Export PDF
    title = (
        f"{data.character_name}'s "
        f"Comic Adventure"
    )

    pdf_path = save_pdf(
        title,
        layout,
    )

    return {
        "title": title,
        "layout": layout,
        "pdf_path": pdf_path,
    }


@router.get("/")
async def home(
    request: Request,
):
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "demo_mode": settings.demo_mode,
        },
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=_validate_text(
                story_prompt,
                "Story prompt",
            ),
            character_name=_validate_text(
                character_name,
                "Character name",
            ),
            setting=_validate_text(
                setting,
                "Setting",
            ),
            tone=_validate_text(
                tone,
                "Tone",
            ),
            art_style=_validate_text(
                art_style,
                "Art style",
            ),
        )

        result = _generate_comic(data)

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context=result,
        )

    except Exception as exc:
        import traceback

        traceback.print_exc()

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc),
                "demo_mode": settings.demo_mode,
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(
    payload: PromptRequest,
):
    try:
        result = _generate_comic(payload)

        return JSONResponse(
            content=result,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/export-success")
async def export_success(
    request: Request,
):
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.get("/test-image")
async def test_image(
    prompt: str = "comic book hero in an enchanted forest",
):
    try:
        path = generate_image(
            prompt,
            999,
        )

        return {
            "success": True,
            "image_path": path,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
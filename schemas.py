from typing import List

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):

    story_prompt: str = Field(
        ...,
        min_length=3,
        max_length=2000
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=80
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=120
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=80
    )


class Panel(BaseModel):

    panel_number: int

    title: str

    scene_description: str

    image_prompt: str

    caption: str = ""

    narration: str = ""

    dialogue: str = ""

    image_path: str = ""


class ComicResult(BaseModel):

    title: str

    panels: List[Panel]

    pdf_path: str = ""
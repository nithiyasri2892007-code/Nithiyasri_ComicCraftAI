# filepath: c:\Users\34 SYS\Documents\ComicCraftAI\app\exporters.py
from pathlib import Path
from uuid import uuid4

from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parent.parent

EXPORTS_DIR = BASE_DIR / "static" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_text(text) -> str:
    return (
        str(text)
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def _split_long_word(pdf: FPDF, word: str, width: float) -> list[str]:
    chunks = []
    current = ""

    for character in word:
        candidate = current + character

        if current and pdf.get_string_width(candidate) > width:
            chunks.append(current)
            current = character
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks or [""]


def _wrap_text(pdf: FPDF, text: str, width: float) -> str:
    text = _safe_text(text)
    wrapped_lines = []

    for paragraph in text.splitlines() or [""]:
        if not paragraph:
            wrapped_lines.append("")
            continue

        current_line = ""

        for word in paragraph.split():
            if pdf.get_string_width(word) > width:
                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = ""

                wrapped_lines.extend(
                    _split_long_word(pdf, word, width)
                )
                continue

            candidate = (
                word
                if not current_line
                else f"{current_line} {word}"
            )

            if pdf.get_string_width(candidate) <= width:
                current_line = candidate
            else:
                wrapped_lines.append(current_line)
                current_line = word

        if current_line:
            wrapped_lines.append(current_line)

    return "\n".join(wrapped_lines)


def _write_text(
    pdf: FPDF,
    text,
    width: float,
    height: float,
) -> None:
    width = max(float(width), 1)

    pdf.set_x(pdf.l_margin)

    pdf.multi_cell(
        width,
        height,
        _wrap_text(pdf, text, width),
    )


def save_pdf(
    title: str,
    layout: list[dict],
):
    filename = f"comic_{uuid4().hex[:10]}.pdf"
    path = EXPORTS_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    usable_width = pdf.w - pdf.l_margin - pdf.r_margin

    for panel in layout:
        pdf.add_page()

        # -------------------------
        # Panel title
        # -------------------------

        pdf.set_font("Helvetica", "B", 18)

        _write_text(
            pdf,
            f"{title} - Panel {panel.get('panel_number', '')}",
            usable_width,
            10,
        )

        pdf.ln(2)

        # -------------------------
        # Panel image
        # -------------------------

        image_url = panel.get("image_path", "")

        if (
            isinstance(image_url, str)
            and image_url.startswith("/static/")
        ):
            image_path = (
                BASE_DIR
                / image_url.removeprefix("/static/")
            )

            if image_path.exists():
                pdf.image(
                    str(image_path),
                    x=pdf.l_margin,
                    y=None,
                    w=usable_width,
                )
                pdf.ln(5)

        # -------------------------
        # Panel heading
        # -------------------------

        pdf.set_font("Helvetica", "B", 12)

        title_text = panel.get("title", "")

        if title_text:
            _write_text(
                pdf,
                title_text,
                usable_width,
                7,
            )

        # -------------------------
        # Scene description
        # -------------------------

        scene_description = panel.get(
            "scene_description",
            "",
        )

        if scene_description:
            pdf.set_font("Helvetica", "I", 10)

            _write_text(
                pdf,
                scene_description,
                usable_width,
                6,
            )

            pdf.ln(2)

        # -------------------------
        # Caption / narration /
        # dialogue
        # -------------------------

        for label in (
            "caption",
            "narration",
            "dialogue",
        ):
            value = panel.get(label, "")

            if not value:
                continue

            pdf.set_font("Helvetica", "B", 11)

            _write_text(
                pdf,
                f"{label.capitalize()}:",
                usable_width,
                6,
            )

            pdf.set_font("Helvetica", "", 11)

            _write_text(
                pdf,
                value,
                usable_width,
                6,
            )

            pdf.ln(1)

    pdf.output(str(path))

    return f"/static/exports/{filename}"
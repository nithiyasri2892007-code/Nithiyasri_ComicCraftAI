def build_comic_layout(
    outline,
    story_panels,
    image_paths
):

    story_by_number = {
        panel["panel_number"]: panel
        for panel in story_panels
    }

    layout = []

    for item in outline:

        number = item["panel_number"]

        story = story_by_number.get(
            number,
            {}
        )

        layout.append(
            {
                "panel_number": number,

                "title": item.get(
                    "title",
                    f"Panel {number}"
                ),

                "scene_description": item.get(
                    "scene_description",
                    ""
                ),

                "image_prompt": item.get(
                    "image_prompt",
                    ""
                ),

                "caption": story.get(
                    "caption",
                    ""
                ),

                "narration": story.get(
                    "narration",
                    ""
                ),

                "dialogue": story.get(
                    "dialogue",
                    ""
                ),

                "image_path": image_paths.get(
                    number,
                    ""
                ),
            }
        )

    return layout
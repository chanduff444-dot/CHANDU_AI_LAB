def render_snake_html(render_dict):
    """
    Converts a Snake render_dict into an HTML grid string.
    Returns raw HTML — pass with  unsafe_allow_html=True  in Streamlit.
    """
    snake_set = set(map(tuple, render_dict["snake"]))
    head      = tuple(render_dict["head"]) if render_dict["head"] else None
    food      = tuple(render_dict["food"])
    width     = render_dict["width"]
    height    = render_dict["height"]
    score     = render_dict["score"]
    done      = render_dict["done"]

    CELL = 40   # px

    COLOR = {
        "head":  "#1a73e8",
        "body":  "#0d47a1",
        "food":  "#e53935",
        "empty": "#111111",
    }

    rows_html = ""
    for y in range(height):
        cells = ""
        for x in range(width):
            pos = (x, y)
            if pos == head:
                bg   = COLOR["head"]
                icon = "■"
                size = "20px"
                color = "#ffffff"
            elif pos in snake_set:
                bg   = COLOR["body"]
                icon = "■"
                size = "16px"
                color = "#90caf9"
            elif pos == food:
                bg   = COLOR["empty"]
                icon = "●"
                size = "18px"
                color = "#ef5350"
            else:
                bg   = COLOR["empty"]
                icon = ""
                size = "0"
                color = "transparent"

            cells += (
                f'<td style="'
                f'width:{CELL}px;height:{CELL}px;'
                f'background:{bg};'
                f'text-align:center;vertical-align:middle;'
                f'font-size:{size};color:{color};'
                f'border:1px solid #1a1a1a;'
                f'">{icon}</td>'
            )
        rows_html += f"<tr>{cells}</tr>"

    status = "GAME OVER" if done else f"Score: {score}"
    status_color = "#ef5350" if done else "#9aa0a6"

    return (
        f'<div style="display:inline-block;background:#0d0d0d;'
        f'padding:14px;border-radius:10px;border:1px solid #2a2a2a;">'
        f'<div style="color:{status_color};font-size:12px;'
        f'margin-bottom:8px;font-family:sans-serif;letter-spacing:1px;">'
        f'{status}</div>'
        f'<table style="border-collapse:collapse;">{rows_html}</table>'
        f'</div>'
    )
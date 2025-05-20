import clipboard


def text_from_clipboard() -> str:
    url = str(clipboard.paste())
    return url

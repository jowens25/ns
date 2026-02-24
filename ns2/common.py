
def formatListToString(elements: list[str]) -> str:
    if len(elements) == 0:
        return None
    return ', '.join(elements) if elements else ''
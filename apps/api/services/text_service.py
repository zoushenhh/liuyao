from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

TEXTS_MAP = {
    "text": "占诀",
    "example": "古占例",
    "update": "日志",
}


def list_texts() -> list[dict]:
    return [{"name": k, "title": v} for k, v in TEXTS_MAP.items()]


def get_text(name: str) -> dict | None:
    if name not in TEXTS_MAP:
        return None

    path = ROOT / f"{name}.md"
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8")
    return {"name": name, "title": TEXTS_MAP[name], "content": content}

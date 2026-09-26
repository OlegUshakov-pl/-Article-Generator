import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import ollama
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
ARTICLES_DIR = BASE_DIR / "articles"
STATIC_DIR = BASE_DIR / "static"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "model": "qwen2.5:7b",
    "temperature": 0.7,
    "system_prompt": "Ты полезный ассистент, который пишет качественные статьи.",
    "num_predict": 1000,
    "target_server_url": "",
}

app = FastAPI(title="Article Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------- settings


def read_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)
    merged = dict(DEFAULT_SETTINGS)
    merged.update({k: v for k, v in data.items() if v is not None})
    return merged


def write_settings(data: dict) -> dict:
    merged = dict(DEFAULT_SETTINGS)
    merged.update({k: v for k, v in data.items() if v is not None})
    SETTINGS_FILE.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return merged


def article_path(article_id: str) -> Path:
    if not article_id or ".." in article_id or "/" in article_id or "\\" in article_id:
        raise HTTPException(status_code=400, detail="Некорректный id статьи")
    path = ARTICLES_DIR / f"{article_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return path


def load_article(article_id: str) -> dict:
    try:
        return json.loads(article_path(article_id).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        raise HTTPException(status_code=500, detail="Не удалось прочитать статью")


def save_article(data: dict) -> None:
    path = ARTICLES_DIR / f"{data['id']}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# -------------------------------------------------------------------- models


class SettingsIn(BaseModel):
    model: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None
    num_predict: Optional[int] = None
    target_server_url: Optional[str] = None


class GenerateIn(BaseModel):
    prompt: str


class ArticleCreate(BaseModel):
    title: str = ""
    content: str = ""
    prompt: str = ""


class ArticleUpdate(BaseModel):
    title: str = ""
    content: str = ""


# ----------------------------------------------------------------- settings


@app.get("/api/settings")
def get_settings() -> dict:
    return read_settings()


@app.post("/api/settings")
def post_settings(body: SettingsIn) -> dict:
    return write_settings(body.model_dump())


@app.get("/api/models")
def get_models() -> dict:
    try:
        result = ollama.list()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama недоступна. Запустите её (ollama serve). Детали: {exc}",
        )
    models = []
    for m in getattr(result, "models", []) or []:
        name = getattr(m, "model", None) or getattr(m, "name", None)
        if name:
            models.append({"name": name})
    return {"models": models}


# ----------------------------------------------------------------- generate


def _error_stream(message: str):
    def gen():
        yield f"\n\n[ОШИБКА] {message}"

    return gen()


def _chunk_content(chunk) -> str:
    if isinstance(chunk, dict):
        message = chunk.get("message")
        return message.get("content", "") if isinstance(message, dict) else ""
    message = getattr(chunk, "message", None)
    return getattr(message, "content", "") or ""


@app.post("/api/generate")
def generate(body: GenerateIn) -> StreamingResponse:
    settings = read_settings()
    prompt = (body.prompt or "").strip()
    if not prompt:
        raise HTTPException(
            status_code=400, detail="Описание статьи не может быть пустым"
        )

    messages = []
    system_prompt = (settings.get("system_prompt") or "").strip()
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    options = {
        "temperature": float(settings.get("temperature", 0.7)),
        "num_predict": int(settings.get("num_predict", 1000)),
    }

    try:
        stream = ollama.chat(
            model=settings.get("model") or DEFAULT_SETTINGS["model"],
            messages=messages,
            stream=True,
            options=options,
        )
    except Exception as exc:
        return StreamingResponse(
            _error_stream(
                "Не удалось подключиться к Ollama. Убедитесь, что она запущена "
                f"(ollama serve). Детали: {exc}"
            ),
            media_type="text/plain; charset=utf-8",
            headers={"X-Stream-Error": "1"},
        )

    def event_stream():
        try:
            for chunk in stream:
                content = _chunk_content(chunk)
                if content:
                    yield content
        except Exception as exc:
            yield f"\n\n[ОШИБКА] Ошибка генерации: {exc}"

    return StreamingResponse(
        event_stream(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ----------------------------------------------------------------- articles


@app.get("/api/articles")
def list_articles() -> list:
    items = []
    if ARTICLES_DIR.exists():
        for path in ARTICLES_DIR.glob("*.json"):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
    items.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    return items


@app.post("/api/articles", status_code=201)
def create_article(body: ArticleCreate) -> dict:
    now = datetime.now().isoformat(timespec="seconds")
    data = {
        "id": str(uuid.uuid4()),
        "title": body.title.strip() or "Без названия",
        "content": body.content,
        "prompt": body.prompt,
        "created_at": now,
        "updated_at": now,
    }
    save_article(data)
    return data


@app.get("/api/articles/{article_id}")
def get_article(article_id: str) -> dict:
    return load_article(article_id)


@app.put("/api/articles/{article_id}")
def update_article(article_id: str, body: ArticleUpdate) -> dict:
    data = load_article(article_id)
    data["title"] = body.title.strip() or data.get("title") or "Без названия"
    data["content"] = body.content
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    save_article(data)
    return data


@app.delete("/api/articles/{article_id}")
def delete_article(article_id: str) -> dict:
    path = article_path(article_id)
    path.unlink()
    return {"ok": True, "id": article_id}


# --------------------------------------------------------------------- send


@app.post("/api/send/{article_id}")
def send_article(article_id: str) -> dict:
    data = load_article(article_id)
    target = (read_settings().get("target_server_url") or "").strip()
    if not target:
        raise HTTPException(
            status_code=400,
            detail="URL сервера не задан. Укажите его в настройках.",
        )
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(target, json=data)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail=f"Не удалось отправить статью: {exc}"
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Сервер ответил ошибкой {response.status_code}",
        )
    return {"ok": True, "status_code": response.status_code, "target": target}


# ------------------------------------------------------------------- static


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

import httpx
import ollama
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SAVE_DIR = "articles"
DEFAULT_LANGUAGE = "en"
LANGUAGES = ("en", "ru")

DEFAULT_SYSTEM_PROMPTS = {
    "en": "You are a helpful assistant that writes high-quality articles.",
    "ru": "Ты полезный ассистент, который пишет качественные статьи.",
}

MESSAGES = {
    "en": {
        "invalid_article_id": "Invalid article id",
        "article_not_found": "Article not found",
        "read_article_failed": "Failed to read the article",
        "provider_connected": "{name} connected",
        "provider_not_running": "{name} not running",
        "provider_not_installed": "{name} not installed",
        "install_or_choose": "{name} is not installed. Install it or choose another provider.",
        "start_app": "{name} is not running. Open the app and wait for the model to load.",
        "unknown_provider": "Unknown model provider",
        "unknown_language": "Unsupported language",
        "cannot_create_folder": "Cannot create folder: {exc}",
        "no_folder_access": "No access to this folder",
        "cannot_open_folder": "Cannot open the folder: {exc}",
        "empty_prompt": "Article description cannot be empty",
        "no_models": "{name} is running, but no models were found. Download a model.",
        "untitled": "Untitled",
        "target_url_missing": "Target server URL is not set. Set it in settings.",
        "send_failed": "Failed to send the article: {exc}",
        "server_error": "The server responded with an error {status}",
        "error_marker": "[ERROR]",
        "no_content_hint": (
            "\n\n[ERROR] The model spent its entire token budget on internal "
            "reasoning (thinking) and returned no text. Increase Num Predict in "
            "settings (e.g. 2000-4000) or pick a model without reasoning mode."
        ),
    },
    "ru": {
        "invalid_article_id": "Некорректный id статьи",
        "article_not_found": "Статья не найдена",
        "read_article_failed": "Не удалось прочитать статью",
        "provider_connected": "{name} подключена",
        "provider_not_running": "{name} не запущена",
        "provider_not_installed": "{name} не установлена",
        "install_or_choose": "{name} не установлена. Установите её или выберите другой источник.",
        "start_app": "{name} не запущена. Откройте приложение и дождитесь загрузки модели.",
        "unknown_provider": "Неизвестный источник моделей",
        "unknown_language": "Неподдерживаемый язык",
        "cannot_create_folder": "Невозможно создать папку: {exc}",
        "no_folder_access": "Нет доступа к этой папке",
        "cannot_open_folder": "Не удалось открыть папку: {exc}",
        "empty_prompt": "Описание статьи не может быть пустым",
        "no_models": "{name} запущена, но модели не найдены. Загрузите модель.",
        "untitled": "Без названия",
        "target_url_missing": "URL сервера не задан. Укажите его в настройках.",
        "send_failed": "Не удалось отправить статью: {exc}",
        "server_error": "Сервер ответил ошибкой {status}",
        "error_marker": "[ОШИБКА]",
        "no_content_hint": (
            "\n\n[ОШИБКА] Модель потратила весь лимит токенов на внутренние рассуждения "
            "(thinking) и не вернула текст. Увеличьте Num Predict в настройках "
            "(например 2000–4000) или выберите модель без режима reasoning."
        ),
    },
}

DEFAULT_SETTINGS = {
    "provider": "ollama",
    "model": "qwen2.5:7b",
    "temperature": 0.7,
    "system_prompt": DEFAULT_SYSTEM_PROMPTS[DEFAULT_LANGUAGE],
    "num_predict": 1000,
    "target_server_url": "",
    "save_dir": DEFAULT_SAVE_DIR,
    "language": DEFAULT_LANGUAGE,
}


def t(key: str, **fmt) -> str:
    lang = read_settings().get("language") or DEFAULT_LANGUAGE
    table = MESSAGES.get(lang) or MESSAGES[DEFAULT_LANGUAGE]
    text = table.get(key) or MESSAGES[DEFAULT_LANGUAGE].get(key) or key
    return text.format(**fmt) if fmt else text

PROVIDERS = (
    {"id": "ollama", "name": "Ollama"},
    {"id": "lmstudio", "name": "LM Studio"},
)

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
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    articles_dir()


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
    if "system_prompt" not in data:
        merged["system_prompt"] = DEFAULT_SYSTEM_PROMPTS.get(
            merged.get("language") or DEFAULT_LANGUAGE,
            DEFAULT_SYSTEM_PROMPTS[DEFAULT_LANGUAGE],
        )
    if merged.get("language") not in LANGUAGES:
        merged["language"] = DEFAULT_LANGUAGE
    return merged


def write_settings(data: dict) -> dict:
    merged = read_settings()
    merged.update({k: v for k, v in data.items() if v is not None})
    SETTINGS_FILE.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return merged


def resolve_dir(raw: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(str(raw or "").strip()))
    path = Path(expanded or DEFAULT_SAVE_DIR)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def articles_dir() -> Path:
    raw = str(read_settings().get("save_dir") or DEFAULT_SAVE_DIR).strip()
    path = resolve_dir(raw or DEFAULT_SAVE_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def article_path(article_id: str, folder: Optional[Path] = None) -> Path:
    if not article_id or ".." in article_id or "/" in article_id or "\\" in article_id:
        raise HTTPException(status_code=400, detail=t("invalid_article_id"))
    path = (folder or articles_dir()) / f"{article_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=t("article_not_found"))
    return path


def load_article(article_id: str) -> dict:
    try:
        return json.loads(article_path(article_id).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        raise HTTPException(status_code=500, detail=t("read_article_failed"))


def save_article(data: dict) -> None:
    path = articles_dir() / f"{data['id']}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------- providers


def _ollama_host() -> str:
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").strip()
    if host and not host.startswith(("http://", "https://")):
        host = "http://" + host
    return host.rstrip("/")


def _lmstudio_host() -> str:
    host = os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234").strip()
    if host and not host.startswith(("http://", "https://")):
        host = "http://" + host
    return host.rstrip("/")


def _running(url: str) -> bool:
    try:
        with httpx.Client(timeout=2.0) as client:
            return client.get(url).status_code == 200
    except httpx.HTTPError:
        return False


def _existing(paths) -> bool:
    return any(p and Path(p).exists() for p in paths)


def ollama_installed() -> bool:
    if shutil.which("ollama"):
        return True
    local = os.environ.get("LOCALAPPDATA") or ""
    home = Path.home()
    return _existing(
        [
            (Path(local) / "Programs" / "Ollama" / "ollama.exe") if local else None,
            (Path(local) / "Ollama" / "ollama.exe") if local else None,
            "/usr/local/bin/ollama",
            "/usr/bin/ollama",
            "/opt/homebrew/bin/ollama",
            home / ".local" / "bin" / "ollama",
            "/Applications/Ollama.app/Contents/MacOS/Ollama",
        ]
    )


def lmstudio_installed() -> bool:
    if shutil.which("lms") or shutil.which("lmstudio"):
        return True
    local = os.environ.get("LOCALAPPDATA") or ""
    home = Path.home()
    return _existing(
        [
            (Path(local) / "Programs" / "LM Studio" / "LM Studio.exe") if local else None,
            (Path(local) / "Programs" / "lm-studio" / "LM Studio.exe") if local else None,
            home / "Applications" / "LM Studio.app",
            "/Applications/LM Studio.app",
        ]
    )


def ollama_models() -> list:
    host = _ollama_host()
    try:
        with httpx.Client(timeout=5.0) as client:
            data = client.get(f"{host}/api/tags").json()
        names = [m.get("model") or m.get("name") for m in data.get("models", []) or []]
        if any(names):
            return [n for n in names if n]
    except (httpx.HTTPError, ValueError):
        pass
    try:
        result = ollama.list()
    except Exception:
        return []
    names = []
    for m in getattr(result, "models", []) or []:
        name = getattr(m, "model", None) or getattr(m, "name", None)
        if name:
            names.append(name)
    return names


def lmstudio_models() -> list:
    try:
        with httpx.Client(timeout=5.0) as client:
            data = client.get(f"{_lmstudio_host()}/v1/models").json()
    except (httpx.HTTPError, ValueError):
        return []
    names = []
    for m in data.get("data", []) or []:
        name = m.get("id") or m.get("name")
        if name:
            names.append(name)
    return names


def provider_state(provider_id: str) -> dict:
    meta = next((p for p in PROVIDERS if p["id"] == provider_id), PROVIDERS[0])
    if provider_id == "lmstudio":
        installed, running = lmstudio_installed(), _running(f"{_lmstudio_host()}/v1/models")
        models = lmstudio_models() if running else []
    else:
        installed, running = ollama_installed(), _running(f"{_ollama_host()}/api/tags")
        models = ollama_models() if running else []

    if running:
        status, message = "ready", t("provider_connected", name=meta["name"])
    elif installed:
        status, message = "not_running", t("provider_not_running", name=meta["name"])
    else:
        status, message = "not_installed", t("provider_not_installed", name=meta["name"])

    return {
        "id": meta["id"],
        "name": meta["name"],
        "installed": installed,
        "running": running,
        "status": status,
        "message": message,
        "models": models,
    }


def require_provider(provider_id: str) -> dict:
    state = provider_state(provider_id)
    if state["status"] == "not_installed":
        raise HTTPException(
            status_code=503,
            detail=t("install_or_choose", name=state["name"]),
        )
    if state["status"] == "not_running":
        raise HTTPException(
            status_code=503,
            detail=t("start_app", name=state["name"]),
        )
    return state


# -------------------------------------------------------------------- models


class SettingsIn(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None
    num_predict: Optional[int] = None
    target_server_url: Optional[str] = None
    save_dir: Optional[str] = None
    language: Optional[str] = None


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
    data = body.model_dump(exclude_unset=True)

    target = data.get("target_server_url")
    if target is not None:
        data["target_server_url"] = str(target).strip()

    if data.get("provider") is not None:
        if data["provider"] not in {p["id"] for p in PROVIDERS}:
            raise HTTPException(status_code=400, detail=t("unknown_provider"))

    if data.get("language") is not None:
        if str(data["language"]).lower() not in LANGUAGES:
            raise HTTPException(status_code=400, detail=t("unknown_language"))
        data["language"] = str(data["language"]).lower()

    if data.get("model") is not None and not str(data["model"]).strip():
        data.pop("model")

    if data.get("num_predict") is not None:
        value = int(data["num_predict"])
        if value <= 0:
            data["num_predict"] = 0
        else:
            data["num_predict"] = min(max(value, NUM_PREDICT_MIN), NUM_PREDICT_MAX)

    raw_dir = data.get("save_dir")
    if raw_dir is not None:
        raw_dir = str(raw_dir).strip() or DEFAULT_SAVE_DIR
        data["save_dir"] = raw_dir
        new_dir = resolve_dir(raw_dir)
        try:
            new_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise HTTPException(
                status_code=400, detail=t("cannot_create_folder", exc=exc)
            )
        old_raw = str(read_settings().get("save_dir") or DEFAULT_SAVE_DIR).strip()
        old_dir = resolve_dir(old_raw or DEFAULT_SAVE_DIR)
        if old_dir.resolve() != new_dir.resolve() and old_dir.exists():
            for file in old_dir.glob("*.json"):
                if not (new_dir / file.name).exists():
                    shutil.move(str(file), str(new_dir / file.name))

    return write_settings(data)


@app.get("/api/providers")
def get_providers() -> dict:
    return {
        "providers": [provider_state(p["id"]) for p in PROVIDERS],
        "current": read_settings().get("provider") or "ollama",
    }


@app.get("/api/models")
def get_models(provider: Optional[str] = Query(default=None)) -> dict:
    current = provider or read_settings().get("provider") or "ollama"
    state = provider_state(current)
    return {
        "provider": state["id"],
        "status": state["status"],
        "message": state["message"],
        "models": [{"name": n} for n in state["models"]],
    }


# ----------------------------------------------------------------- fs browse


@app.get("/api/fs/list")
def fs_list(path: str = Query(default="")) -> dict:
    raw = (path or "").strip()
    target = Path(os.path.expandvars(os.path.expanduser(raw))) if raw else BASE_DIR
    if not target.is_absolute():
        target = BASE_DIR / target
    if not target.is_dir():
        target = BASE_DIR
    try:
        children = sorted(
            (
                c
                for c in target.iterdir()
                if c.is_dir() and not c.name.startswith(".") and c.name != "__pycache__"
            ),
            key=lambda c: c.name.lower(),
        )
        dirs = [{"name": c.name, "path": str(c)} for c in children]
    except PermissionError:
        raise HTTPException(status_code=403, detail=t("no_folder_access"))
    except OSError as exc:
        raise HTTPException(status_code=400, detail=t("cannot_open_folder", exc=exc))

    parent = target.parent
    return {
        "path": str(target),
        "parent": str(parent) if parent != target else None,
        "root": str(BASE_DIR),
        "dirs": dirs,
    }


# ----------------------------------------------------------------- generate


NO_CONTENT_HINT_KEY = "no_content_hint"

NUM_PREDICT_MIN = 64
NUM_PREDICT_MAX = 200000


def _num_predict(settings: dict) -> int:
    """0/отрицательное значение в настройках = без лимита -> -1 для бэкендов."""
    try:
        value = int(settings.get("num_predict", 1000))
    except (TypeError, ValueError):
        value = 1000
    if value <= 0:
        return -1
    return min(max(value, NUM_PREDICT_MIN), NUM_PREDICT_MAX)



def _chunk_parts(chunk) -> tuple:
    if isinstance(chunk, dict):
        message = chunk.get("message")
        if not isinstance(message, dict):
            return "", ""
        return message.get("content", "") or "", message.get("thinking", "") or ""
    message = getattr(chunk, "message", None)
    if message is None:
        return "", ""
    if isinstance(message, dict):
        return message.get("content", "") or "", message.get("thinking", "") or ""
    return (
        getattr(message, "content", "") or "",
        getattr(message, "thinking", "") or "",
    )


def stream_ollama(settings: dict, messages: list) -> Iterator[str]:
    stream = ollama.chat(
        model=settings.get("model") or DEFAULT_SETTINGS["model"],
        messages=messages,
        stream=True,
        options={
            "temperature": float(settings.get("temperature", 0.7)),
            "num_predict": _num_predict(settings),
        },
    )
    got_content = False
    got_thinking = False
    for chunk in stream:
        content, thinking = _chunk_parts(chunk)
        if thinking:
            got_thinking = True
        if content:
            got_content = True
            yield content
    if not got_content and got_thinking:
        yield t(NO_CONTENT_HINT_KEY)


def stream_lmstudio(settings: dict, messages: list) -> Iterator[str]:
    payload = {
        "model": settings.get("model"),
        "messages": messages,
        "temperature": float(settings.get("temperature", 0.7)),
        "max_tokens": _num_predict(settings),
        "stream": True,
    }
    got_content = False
    got_thinking = False
    with httpx.Client(timeout=None) as client:
        with client.stream(
            "POST", f"{_lmstudio_host()}/v1/chat/completions", json=payload
        ) as response:
            if response.status_code >= 400:
                body = response.read().decode(errors="replace")[:400]
                raise RuntimeError(
                    f"LM Studio returned error {response.status_code}: {body}"
                )
            for line in response.iter_lines():
                line = line.strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = obj.get("choices") or [{}]
                delta = choices[0].get("delta") or {}
                if delta.get("reasoning_content") or delta.get("reasoning"):
                    got_thinking = True
                content = delta.get("content")
                if content:
                    got_content = True
                    yield content
    if not got_content and got_thinking:
        yield t(NO_CONTENT_HINT_KEY)


@app.post("/api/generate")
def generate(body: GenerateIn) -> StreamingResponse:
    prompt = (body.prompt or "").strip()
    if not prompt:
        raise HTTPException(
            status_code=400, detail=t("empty_prompt")
        )

    settings = read_settings()
    provider = settings.get("provider") or "ollama"
    state = require_provider(provider)
    if not state["models"]:
        raise HTTPException(
            status_code=400,
            detail=t("no_models", name=state["name"]),
        )
    if settings.get("model") not in state["models"]:
        settings["model"] = state["models"][0]

    messages = []
    system_prompt = (settings.get("system_prompt") or "").strip()
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    if provider == "lmstudio":
        stream = stream_lmstudio(settings, messages)
    else:
        stream = stream_ollama(settings, messages)

    def event_stream():
        try:
            yield from stream
        except Exception as exc:
            yield f"\n\n{t('error_marker')} {exc}"

    return StreamingResponse(
        event_stream(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ----------------------------------------------------------------- articles


@app.get("/api/articles")
def list_articles() -> list:
    folder = articles_dir()
    items = []
    for path in folder.glob("*.json"):
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
        "title": body.title.strip() or t("untitled"),
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
    data["title"] = body.title.strip() or data.get("title") or t("untitled")
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
            detail=t("target_url_missing"),
        )
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(target, json=data)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail=t("send_failed", exc=exc)
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=t("server_error", status=response.status_code),
        )
    return {"ok": True, "status_code": response.status_code, "target": target}


# ------------------------------------------------------------------- static


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")

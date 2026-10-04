# Article Generator

A local web service for generating articles: describe a topic → the model writes text in real time → edit it in the editor → save, export, or send it to another server.

Works without internet (except for the Tailwind and Quill CDNs), without a database, without authorization, and without payment.

---

## Features

| Page | Capabilities |
|---|---|
| **Create** (`/static/index.html`) | Description → streaming response from Ollama / LM Studio right into the Rich Text Editor (Quill) → title → save |
| **Articles** (`static/articles.html`) | Cards with all articles, preview, open, delete with confirmation |
| **Article** (`/static/article.html`) | Edit title and text, export to `.json` / `.md` / `.txt`, send to an external server |
| **Settings** (`/static/settings.html`) | Model provider (Ollama / LM Studio), model selection, article storage folder, temperature, num predict, system prompt, target server URL |

---

## Requirements

* **Python 3.10+** (check: `python --version`)
* **Ollama** and/or **LM Studio** — at least one model provider
* A browser (Chrome, Edge, Firefox, Safari)

---

## Installing a Model Provider

### Option 1 — Ollama

1. Download and install: <https://ollama.com/download>
2. Launch the app (tray icon) or run in the terminal:
   ```bash
   ollama serve
   ```
3. Pull a model, for example:
   ```bash
   ollama pull qwen2.5:7b
   ```
   Other options: `llama3.2:3b`, `mistral:7b`, `gemma2:9b`, `qwen2.5:14b`.

The server listens on `http://127.0.0.1:11434` by default.
A different address can be set via the `OLLAMA_HOST` environment variable.

### Option 2 — LM Studio

1. Download and install: <https://lmstudio.ai>
2. Launch LM Studio → **Developer** tab (or server icon) → click **Start Server**.
3. Load any model (GGUF) via the **Search** tab.

The OpenAI-compatible server runs on `http://127.0.0.1:1234` by default.
A different address can be set via the `LMSTUDIO_BASE_URL` environment variable.

> If the program is not running or not installed, the settings page will say so directly:
> "Ollama not installed", "Ollama not running", "LM Studio not installed", "LM Studio not running".

---

## Running

### Quick way (Windows)

Double-click **`start.bat`** — the script will create a virtual environment, install dependencies, and start the server at <http://127.0.0.1:8000>.

### Manual way

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
uvicorn main:app --reload
```

Stop the server: `Ctrl+C`.

---

## Settings to Check First

Open **Settings**:

1. **Model provider** — choose Ollama or LM Studio (the card will highlight, with the status next to it). Click "🔄 Refresh" if you launched the app after opening the page.
2. **Model** — list of models from the selected provider. Click **💾 Save**.
3. **Where to store articles** — a folder on disk. You can enter a path manually (`D:\MyArticles`), use "📂 Browse…" or the quick `articles` button. When changing the folder, already saved articles **move** to the new one.
4. **Temperature** — from 0 (precise) to 2 (creative), usually 0.6–0.9.
5. **Num Predict** — maximum tokens in the response: from 64 to 200000, or `0` for no limit (the model writes as much as needed, up to filling the context).
6. **System Prompt** — the model's role and style.
7. **Target Server URL** — *optional*. The address used by the "Send to server" button (`https://example.com/api/receive`). If the field is empty, the "Send to server" button on the article page will be disabled — articles are simply stored in the folder.

All values are stored in `settings.json` in the project root.

---

## Data Storage

* **Articles** — one JSON file per article: `{id}.json`
* **Settings** — `settings.json`
* No database, everything is plain files

Article format:

```json
{
  "id": "uuid",
  "title": "Title",
  "content": "<p>HTML from the editor</p>",
  "prompt": "Original description",
  "created_at": "2026-05-13T10:00:00",
  "updated_at": "2026-05-13T10:00:00"
}
```

---

## Export

On the article page, select a format from the dropdown next to the "Export" button:

| Format | Contents |
|---|---|
| `.json` | Full article object (title, content, prompt, dates) |
| `.md` | Markdown: headings, lists, quotes, bold, italic, links, code |
| `.txt` | Plain text without markup |

The file downloads as `article_{id}.{extension}`.

---

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/providers` | Ollama / LM Studio status + model lists |
| `GET` | `/api/models` | Models of the selected provider |
| `GET` `/POST` | `/api/settings` | Read and write settings |
| `POST` | `/api/generate` | Streaming text from the model (`{"prompt": "..."}`) |
| `GET` | `/api/articles` | List of articles (newest first) |
| `POST` | `/api/articles` | Create an article (`{title, content, prompt}`) |
| `GET` `/PUT` `/DELETE` | `/api/articles/{id}` | Read, update, delete |
| `POST` | `/api/send/{id}` | Send an article to `target_server_url` |
| `GET` | `/api/fs/list?path=` | Subfolders for choosing a storage location |
| `GET` | `/` | Redirect to `/static/index.html` |

Interactive documentation: <http://127.0.0.1:8000/docs>

---

## Tech Stack

* **Backend** — FastAPI + Uvicorn, `ollama` and `httpx` libraries
* **Frontend** — vanilla HTML / JS, Tailwind CSS (CDN), Quill.js 2.0.3 (CDN)
* **Storage** — file system, no database

---

## Troubleshooting

| Symptom | What to do |
|---|---|
| "Ollama not installed" / "LM Studio not installed" | Install the app or choose another provider |
| "Ollama not running" | Start Ollama / `ollama serve`, then click "🔄 Refresh" on the settings page |
| "LM Studio not running" | In LM Studio open the Developer tab → **Start Server** |
| Empty model list | Pull a model (`ollama pull ...` or via the Search tab in LM Studio) |
| "Send to server" button is grey and unclickable | Fill in Target Server URL in settings (the field is optional) |
| Port 8000 is busy | `uvicorn main:app --port 8001` or free up the port |
| Page does not open | Check that the terminal window is not closed and the server is running |

---

## Project Structure

```
main.py            # FastAPI: API, streaming, providers, file storage
start.bat          # Windows launcher (venv + dependencies + uvicorn)
requirements.txt   # fastapi, uvicorn, ollama, httpx
settings.json      # Settings (created automatically)
articles/          # Default articles folder (path can be changed in settings)
static/
  index.html       # Create article
  articles.html    # Articles list
  article.html     # Edit and export
  settings.html    # Settings
```

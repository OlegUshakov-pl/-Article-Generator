# Техническое задание: Приложение-генератор статей на Ollama

## Цель
Сделать веб-приложение для генерации текстов с помощью локальной Ollama из описания. Без авторизации и оплаты на первом этапе.

## Стек (обязательно)
- Backend: FastAPI (Python) устанавливается в VENV
- Frontend: Чистый HTML + JavaScript + Tailwind CSS via CDN (`https://cdn.tailwindcss.com`)
- Редактор текста: RichTextEditor - обязательно. Используй Quill.js via CDN (https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css и quill.js) или Toast UI Editor или TinyMCE CDN. Предпочтение Quill.js - самый легкий для подключения.
- LLM: Ollama (python library `ollama`)
- Хранение: Файловая система. Статьи в папке `articles/` как отдельные JSON файлы. Настройки в `settings.json` в корне.
- Базы данных НЕ использовать.

## Дизайн (ОБЯЗАТЕЛЬНО - КРАСИВЫЙ, СВЕТЛЫЙ)
- Тема: ТОЛЬКО светлая, светлый фон #f9fafb или #ffffff, карточки белые с мягкой тенью `shadow-sm` / `shadow-lg`
- Стиль: Современный минимализм, много воздуха, скругления `rounded-xl` / `rounded-2xl`, аккуратные бордеры `border-gray-200`
- Цвета: Светлый фон, белый контент, акцентный цвет - indigo-600 / violet-600 для кнопок, серый текст gray-600
- Навигация: Верхний хедер с логотипом и ссылками: Создать | Статьи | Настройки. Хедер белый, sticky.
- Кнопки: Красивые, с hover эффектами, `transition-all`, `rounded-lg`
- Инпуты: Светлые, с `focus:ring-2 focus:ring-indigo-500`
- Страницы должны выглядеть как современный SaaS, а не как админка из 2010. Используй иконки (можно emoji или heroicons via CDN).
- ОБЯЗАТЕЛЬНО добавь красивые empty states, лоадеры, toast уведомления.

## Структура проекта
```
/main.py
/settings.json
/articles/  # папка создается автоматически
/static/
  index.html      # Страница создания статьи
  articles.html   # Страница списка статей
  article.html    # Страница одной статьи
  settings.html   # Страница настроек
```

## Страницы и функционал

### 1. `static/index.html` - Создание статьи
- Поле textarea: "Описание статьи" (prompt) - красивое светлое поле
- Кнопка "Сгенерировать ✨" - большая, indigo-600
- Результат: ОБЯЗАТЕЛЬНО RichTextEditor (Quill.js). Сюда стримится ответ от Ollama в реальном времени. При стриминге вставлять HTML в Quill через `quill.setText()` или `quill.clipboard.dangerouslyPasteHTML()` с накоплением. Должен быть форматированный текст (заголовки, списки, жирный).
- Поле "Заголовок статьи" - input
- Кнопка "Сохранить" -> сохраняет в `articles/{uuid}.json`. Контент сохранять как HTML из Quill (`quill.root.innerHTML`)
- Дизайн: Светлый SaaS, центрированный контейнер max-w-4xl, карточки белые

### 2. `static/articles.html` - Список статей
- Загружает все json из `/api/articles`
- Отображает в виде красивых светлых карточек в сетке `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`: Заголовок, Дата создания, Превью контента (strip HTML tags, 150 символов)
- Кнопки: Открыть (переход на `/static/article.html?id={id}`), Удалить с подтверждением
- Кнопка "Создать новую"
- Empty state: красивая иллюстрация/иконка "Пока нет статей"

### 3. `static/article.html` - Отдельная статья
- Параметр `?id=` из URL
- Загружает статью `GET /api/articles/{id}`
- Поля редактируемые: Заголовок (input) и Контент - ОБЯЗАТЕЛЬНО RichTextEditor (Quill.js) с тулбаром (жирный, курсив, заголовки H1-H3, списки, цитата, ссылка)
- Контент загружать в Quill: `quill.root.innerHTML = article.content`
- Кнопки:
  1. "Сохранить" -> `PUT /api/articles/{id}` (отправлять `quill.root.innerHTML`)
  2. "Экспорт JSON" -> скачать файл `article_{id}.json` на компьютер (через Blob)
  3. "Выслать на сервер" -> `POST /api/send/{id}`. Показывает красивый toast статуса. URL сервера берется из настроек.
- Дизайн: светлый, редактор большой, на всю ширину карточки

### 4. `static/settings.html` - Настройки
- Дизайн: светлая красивая страница с карточками настроек
- `GET /api/settings` при загрузке, `POST /api/settings` при сохранении
- Поля:
  - Модель Ollama: `<select>` красивый светлый - список из `GET /api/models` (используй `ollama.list()`)
  - Temperature: `<input type="range" min="0" max="2" step="0.1">` с отображением значения
  - System Prompt: textarea светлая
  - Num Predict (max tokens): number input
  - Target Server URL: input type="url" - куда высылать статьи. Обязательное поле. Пример: `https://example.com/api/receive`
- Кнопка Сохранить - indigo-600
- Кнопка Назад

## API Endpoints (main.py)

### GET /api/models
Возвращает список моделей Ollama. Используй `ollama.list()`. Формат: `{"models": [{"name": "qwen2.5:7b"}, ...]}`

### GET /api/settings & POST /api/settings
Чтение/запись `settings.json`. Дефолт если файла нет:
```json
{
  "model": "qwen2.5:7b",
  "temperature": 0.7,
  "system_prompt": "Ты полезный ассистент, который пишет качественные статьи.",
  "num_predict": 1000,
  "target_server_url": ""
}
```

### POST /api/generate
Body: `{"prompt": "описание"}`
- Читает settings.json
- Делает стриминг запрос к Ollama: `ollama.chat(model=settings.model, messages=[system, user], stream=True, options={temperature, num_predict})`
- Возвращает `StreamingResponse` с `text/plain`

### CRUD для статей (хранение в articles/ как JSON)
Формат файла статьи `articles/{id}.json`:
```json
{
  "id": "uuid",
  "title": "Заголовок",
  "content": "Полный текст статьи",
  "prompt": "Исходное описание по которому генерили",
  "created_at": "2026-05-13T10:00:00",
  "updated_at": "2026-05-13T10:00:00"
}
```

- `GET /api/articles` -> список всех статей (отсортировать по created_at desc)
- `POST /api/articles` Body: `{title, content, prompt}` -> создает uuid, сохраняет файл, возвращает объект
- `GET /api/articles/{id}` -> вернуть одну статью
- `PUT /api/articles/{id}` Body: `{title, content}` -> обновить файл, обновить updated_at
- `DELETE /api/articles/{id}` -> удалить файл

### POST /api/send/{id}
- Читает статью из `articles/{id}.json`
- Читает `target_server_url` из settings.json
- Если URL пустой -> вернуть ошибку 400
- Отправляет POST запрос с помощью `httpx` на target_server_url: Body = статья в JSON
- Возвращает результат отправки (status code внешнего сервера)

## Дополнительные требования
1. В `main.py` добавь CORS middleware разрешающий все.
2. Сделай `app.mount("/static", StaticFiles(...))` и редирект с `/` на `/static/index.html`
3. При старте создавать папки `articles/` и `static/` если нет
4. Весь frontend - ванильный JS, без фреймворков. Fetch API.
5. Обработка ошибок: если Ollama не запущена - вернуть понятное сообщение.
6. Код должен запускаться командой `uvicorn main:app --reload`
7. Зависимости: `fastapi, uvicorn, ollama, httpx`

## Что НЕ делать
- Не добавлять авторизацию, платежку, БД
- Не использовать React, Next.js, Vue
- Не использовать базу данных

## Результат
Рабочее приложение где можно: задать описание -> сгенерить текст через Ollama (стриминг) -> сохранить в articles/ -> посмотреть список -> отредактировать -> экспортировать в JSON -> выслать на сервер из настроек.

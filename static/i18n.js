(function () {
  const DICT = {
    en: {
      'nav.create': 'Create',
      'nav.articles': 'Articles',
      'nav.settings': 'Settings',

      'common.save': '💾 Save',
      'common.saving': '⏳ Saving...',
      'common.loading': 'Loading…',
      'common.retry': 'Retry',
      'common.cancel': 'Cancel',
      'common.delete': 'Delete',
      'common.untitled': 'Untitled',
      'common.back': 'Back',
      'common.serverResponded': 'Server responded {n}',
      'common.unknownError': 'Unknown error',

      'doc.index': 'Create Article · Article Generator',
      'doc.articles': 'Articles · Article Generator',
      'doc.article': 'Article · Article Generator',
      'doc.settings': 'Settings · Article Generator',

      'index.h1': 'Create Article',
      'index.sub': 'Describe a topic — Ollama will write the text, and you can edit it in the editor.',
      'index.promptLabel': 'Article description',
      'index.promptPh': 'For example: a detailed article about how local LLMs changed development in 2026, with examples and takeaways...',
      'index.generate': 'Generate',
      'index.generating': 'Generating...',
      'index.clear': 'Clear',
      'index.result': 'Result',
      'index.badge': 'generating...',
      'index.emptyTitle': 'The article text will appear here',
      'index.emptyHint': 'Enter a description above and click "Generate"',
      'index.titleLabel': 'Article title',
      'index.titlePh': 'The title will be used in the articles list',
      'index.toArticles': 'Back to articles',
      'index.quillPh': 'Article text will appear here...',
      'index.needPrompt': 'Enter the article description',
      'index.streaming': 'Streaming the model response…',
      'index.streamingSec': 'Streaming the model response… {s} s',
      'index.thinkingSec': 'The model is thinking… {s} s',
      'index.genError': 'Generation error',
      'index.chars': '{n} characters',
      'index.ollamaError': 'Ollama returned an error — see the text for details',
      'index.generated': 'Article generated',
      'index.emptyResponse': 'Empty response from the model',
      'index.requestFailed': 'Request failed',
      'index.cleared': 'Field cleared',
      'index.needTitle': 'Enter the article title',
      'index.emptyContent': 'The content is empty',
      'index.saveFailed': 'Failed to save the article',
      'index.saved': 'Article saved',

      'articles.h1': 'Articles',
      'articles.total': 'Total: {n} {f}',
      'articles.none': 'No articles yet',
      'articles.new': 'Create new',
      'articles.emptyH': 'No articles yet',
      'articles.emptyP': 'Generate your first article — it will show up here as a card.',
      'articles.emptyBtn': 'Create your first article',
      'articles.loadFailed': 'Failed to load articles',
      'articles.deleteTitle': 'Delete article?',
      'articles.deleteText': 'This cannot be undone — the file will be removed from disk.',
      'articles.open': 'Open',
      'articles.emptyArticle': 'Empty article',
      'articles.deleteFailed': 'Failed to delete the article',
      'articles.deleted': 'Article deleted',
      'articles.one': 'article',
      'articles.few': 'article',
      'articles.many': 'articles',

      'article.back': 'Back to articles',
      'article.titleLabel': 'Title',
      'article.titlePh': 'Article title',
      'article.content': 'Content',
      'article.export': '⬇️ Export',
      'article.exportFormat': 'Export format',
      'article.send': '📤 Send to server',
      'article.unsaved': 'You have unsaved changes',
      'article.notFound': 'Article not found',
      'article.noId': 'No ?id= parameter in the URL',
      'article.missing': 'This article does not exist or it has been deleted.',
      'article.loadError': 'Failed to load the article',
      'article.meta': 'Created: {c} · Updated: {u}',
      'article.needTitle': 'Enter the title',
      'article.saveFailed': 'Failed to save the changes',
      'article.saved': 'Changes saved',
      'article.getFailed': 'Failed to fetch the article',
      'article.downloaded': 'File article_{id}.{fmt} downloaded',
      'article.sending': '⏳ Sending...',
      'article.sendError': 'Error {n}',
      'article.sent': 'Sent to {target} (HTTP {n})',
      'article.sendNoUrl': 'Target server URL is not set — add it in settings',
      'article.quillPh': 'Article content...',

      'settings.h1': 'Settings',
      'settings.sub': 'Model provider, storage location and generation parameters.',
      'settings.langTitle': 'Language',
      'settings.langSub': 'Interface language',
      'settings.providersTitle': 'Model provider',
      'settings.providersSub': 'Choose where your installed models run',
      'settings.refresh': '🔄 Refresh',
      'settings.model': 'Model',
      'settings.storageTitle': 'Where to store articles',
      'settings.storageSub': 'A folder on disk, absolute or relative path',
      'settings.browse': '📂 Browse…',
      'settings.quickDefault': 'articles (default)',
      'settings.genTitle': 'Generation parameters',
      'settings.genSub': 'Temperature and token limit',
      'settings.precise': 'precise',
      'settings.balanced': 'balanced',
      'settings.creative': 'creative',
      'settings.numPredict': 'Num Predict (max tokens)',
      'settings.numPredictRange': 'from 64 to 200000 · 0 = no limit',
      'settings.numPredictHint': 'Enter 0 — the limit is removed and the model writes as much as needed (until the context is full).',
      'settings.systemTitle': 'System Prompt',
      'settings.systemSub': "The model's role and style during generation",
      'settings.systemPh': 'You are a helpful assistant that writes high-quality articles.',
      'settings.targetTitle': 'Target Server URL',
      'settings.targetSub': 'Optional. Where the "Send to server" button posts articles',
      'settings.targetHint': 'Leave it empty if you only need articles in the folder. Example:',
      'settings.back': '← Back',
      'settings.pickerTitle': 'Choose a folder',
      'settings.pickerUp': '↑ Up',
      'settings.pickerRoot': '🏠 Project',
      'settings.pickerSelect': 'Select this folder',
      'settings.pickerLoading': 'Loading…',
      'settings.pickerEmpty': 'No subfolders here',
      'settings.pickerSelected': 'Folder selected',
      'settings.currentValue': 'current value: {v}',
      'settings.noModelsInstalled': '{n} not installed — models unavailable',
      'settings.noModelsRunning': '{n} not running — models unavailable',
      'settings.providerNotFound': 'provider not found',
      'settings.modelsCount': 'models: {n}',
      'settings.loadFailed': 'Failed to load settings',
      'settings.saveFailed': 'Failed to save settings',
      'settings.saved': 'Settings saved',
      'settings.providersFailed': 'Failed to detect model providers: {e}',
      'settings.serverDown': 'The server is not responding',
      'settings.numPredictErr': 'Num Predict: 0 (no limit) or an integer from 64 to 200000',
      'settings.tempErr': 'Temperature: a value from 0 to 2',
      'settings.urlErr': 'Invalid URL. Example: https://example.com/api/receive',
      'settings.modelNotChosen': 'No model selected — the provider is unavailable',
      'settings.modelOne': 'model',
      'settings.modelFew': 'model',
      'settings.modelMany': 'models'
    },
    ru: {
      'nav.create': 'Создать',
      'nav.articles': 'Статьи',
      'nav.settings': 'Настройки',

      'common.save': '💾 Сохранить',
      'common.saving': '⏳ Сохраняем...',
      'common.loading': 'Загрузка…',
      'common.retry': 'Повторить',
      'common.cancel': 'Отмена',
      'common.delete': 'Удалить',
      'common.untitled': 'Без названия',
      'common.back': 'Назад',
      'common.serverResponded': 'Сервер ответил {n}',
      'common.unknownError': 'Неизвестная ошибка',

      'doc.index': 'Создать статью · Article Generator',
      'doc.articles': 'Статьи · Article Generator',
      'doc.article': 'Статья · Article Generator',
      'doc.settings': 'Настройки · Article Generator',

      'index.h1': 'Создать статью',
      'index.sub': 'Опишите тему — Ollama напишет текст, вы сможете отредактировать его в редакторе.',
      'index.promptLabel': 'Описание статьи',
      'index.promptPh': 'Например: подробная статья о том, как локальные LLM изменили разработку в 2026 году, с примерами и выводами...',
      'index.generate': 'Сгенерировать',
      'index.generating': 'Генерируем...',
      'index.clear': 'Очистить',
      'index.result': 'Результат',
      'index.badge': 'генерация...',
      'index.emptyTitle': 'Здесь появится текст статьи',
      'index.emptyHint': 'Введите описание выше и нажмите «Сгенерировать»',
      'index.titleLabel': 'Заголовок статьи',
      'index.titlePh': 'Заголовок будет использован в списке статей',
      'index.toArticles': 'К списку статей',
      'index.quillPh': 'Текст статьи появится здесь...',
      'index.needPrompt': 'Введите описание статьи',
      'index.streaming': 'Стримим ответ модели…',
      'index.streamingSec': 'Стримим ответ модели… {s} с',
      'index.thinkingSec': 'Модель думает… {s} с',
      'index.genError': 'Ошибка генерации',
      'index.chars': '{n} символов',
      'index.ollamaError': 'Ollama вернула ошибку — подробности в тексте',
      'index.generated': 'Статья сгенерирована',
      'index.emptyResponse': 'Пустой ответ от модели',
      'index.requestFailed': 'Не удалось выполнить запрос',
      'index.cleared': 'Поле очищено',
      'index.needTitle': 'Укажите заголовок статьи',
      'index.emptyContent': 'Контент пустой',
      'index.saveFailed': 'Не удалось сохранить статью',
      'index.saved': 'Статья сохранена',

      'articles.h1': 'Статьи',
      'articles.total': 'Всего: {n} {f}',
      'articles.none': 'Статей пока нет',
      'articles.new': 'Создать новую',
      'articles.emptyH': 'Пока нет статей',
      'articles.emptyP': 'Сгенерируйте первую статью — она появится здесь в виде карточки.',
      'articles.emptyBtn': 'Создать первую статью',
      'articles.loadFailed': 'Не удалось загрузить статьи',
      'articles.deleteTitle': 'Удалить статью?',
      'articles.deleteText': 'Действие необратимо — файл будет удалён с диска.',
      'articles.open': 'Открыть',
      'articles.emptyArticle': 'Пустая статья',
      'articles.deleteFailed': 'Не удалось удалить статью',
      'articles.deleted': 'Статья удалена',
      'articles.one': 'статья',
      'articles.few': 'статьи',
      'articles.many': 'статей',

      'article.back': 'Назад к статьям',
      'article.titleLabel': 'Заголовок',
      'article.titlePh': 'Заголовок статьи',
      'article.content': 'Контент',
      'article.export': '⬇️ Экспорт',
      'article.exportFormat': 'Формат экспорта',
      'article.send': '📤 Выслать на сервер',
      'article.unsaved': 'Есть несохранённые изменения',
      'article.notFound': 'Статья не найдена',
      'article.noId': 'В URL не передан параметр ?id=',
      'article.missing': 'Такой статьи не существует или она была удалена.',
      'article.loadError': 'Ошибка загрузки статьи',
      'article.meta': 'Создано: {c} · Обновлено: {u}',
      'article.needTitle': 'Укажите заголовок',
      'article.saveFailed': 'Не удалось сохранить изменения',
      'article.saved': 'Изменения сохранены',
      'article.getFailed': 'Не удалось получить статью',
      'article.downloaded': 'Файл article_{id}.{fmt} скачан',
      'article.sending': '⏳ Отправляем...',
      'article.sendError': 'Ошибка {n}',
      'article.sent': 'Отправлено на {target} (HTTP {n})',
      'article.sendNoUrl': 'URL сервера не задан — укажите его в настройках',
      'article.quillPh': 'Содержимое статьи...',

      'settings.h1': 'Настройки',
      'settings.sub': 'Источник моделей, место хранения и параметры генерации.',
      'settings.langTitle': 'Язык',
      'settings.langSub': 'Язык интерфейса',
      'settings.providersTitle': 'Источник моделей',
      'settings.providersSub': 'Выберите, где запущены установленные модели',
      'settings.refresh': '🔄 Обновить',
      'settings.model': 'Модель',
      'settings.storageTitle': 'Где сохранять статьи',
      'settings.storageSub': 'Папка на диске, абсолютный или относительный путь',
      'settings.browse': '📂 Обзор…',
      'settings.quickDefault': 'articles (по умолчанию)',
      'settings.genTitle': 'Параметры генерации',
      'settings.genSub': 'Температура и лимит токенов',
      'settings.precise': 'точно',
      'settings.balanced': 'сбалансировано',
      'settings.creative': 'творчески',
      'settings.numPredict': 'Num Predict (макс. токенов)',
      'settings.numPredictRange': 'от 64 до 200000 · 0 = без лимита',
      'settings.numPredictHint': 'Укажите 0 — лимит снимется, модель напишет столько, сколько нужно (до заполнения контекста).',
      'settings.systemTitle': 'System Prompt',
      'settings.systemSub': 'Роль и стиль модели при генерации',
      'settings.systemPh': 'Ты полезный ассистент, который пишет качественные статьи.',
      'settings.targetTitle': 'Target Server URL',
      'settings.targetSub': 'Необязательно. Куда отправлять статьи по кнопке «Выслать на сервер»',
      'settings.targetHint': 'Оставьте пустым, если статьи нужны только в папке. Пример:',
      'settings.back': '← Назад',
      'settings.pickerTitle': 'Выбор папки',
      'settings.pickerUp': '↑ Вверх',
      'settings.pickerRoot': '🏠 Проект',
      'settings.pickerSelect': 'Выбрать эту папку',
      'settings.pickerLoading': 'Загрузка…',
      'settings.pickerEmpty': 'В этой папке нет подпапок',
      'settings.pickerSelected': 'Папка выбрана',
      'settings.currentValue': 'текущее значение: {v}',
      'settings.noModelsInstalled': '{n} не установлена — модели недоступны',
      'settings.noModelsRunning': '{n} не запущена — модели недоступны',
      'settings.providerNotFound': 'источник не найден',
      'settings.modelsCount': 'моделей: {n}',
      'settings.loadFailed': 'Не удалось получить настройки',
      'settings.saveFailed': 'Не удалось сохранить настройки',
      'settings.saved': 'Настройки сохранены',
      'settings.providersFailed': 'Не удалось определить источники моделей: {e}',
      'settings.serverDown': 'Сервер не отвечает',
      'settings.numPredictErr': 'Num Predict: 0 (без лимита) или целое число от 64 до 200000',
      'settings.tempErr': 'Temperature: значение от 0 до 2',
      'settings.urlErr': 'Некорректный URL. Пример: https://example.com/api/receive',
      'settings.modelNotChosen': 'Модель не выбрана — источник недоступен',
      'settings.modelOne': 'модель',
      'settings.modelFew': 'модели',
      'settings.modelMany': 'моделей'
    }
  };

  let lang = 'en';
  try {
    const saved = localStorage.getItem('ag_lang');
    if (saved && DICT[saved]) lang = saved;
  } catch (e) {}

  const listeners = [];

  function t(key, vars) {
    const table = DICT[lang] || DICT.en;
    let text = table[key];
    if (text === undefined) text = DICT.en[key];
    if (text === undefined) return key;
    if (vars) {
      for (const k of Object.keys(vars)) {
        text = text.split('{' + k + '}').join(String(vars[k]));
      }
    }
    return text;
  }

  function apply(root) {
    root = root || document;
    const titleKey = document.documentElement.getAttribute('data-title-key');
    if (titleKey) document.title = t(titleKey);
    root.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
    root.querySelectorAll('[data-i18n-ph]').forEach(el => { el.placeholder = t(el.dataset.i18nPh); });
    root.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.dataset.i18nTitle); });
  }

  function setLang(next) {
    if (!DICT[next]) next = 'en';
    lang = next;
    try { localStorage.setItem('ag_lang', next); } catch (e) {}
    document.documentElement.lang = next;
    apply();
    listeners.forEach(fn => { try { fn(next); } catch (e) {} });
  }

  function onChange(fn) { listeners.push(fn); }

  function plural(n, one, few, many) {
    if (lang === 'ru') {
      const a = Math.abs(n) % 100, b = a % 10;
      if (a > 10 && a < 20) return many;
      if (b > 1 && b < 5) return few;
      if (b === 1) return one;
      return many;
    }
    return n === 1 ? one : many;
  }

  function dateLocale() { return lang === 'ru' ? 'ru-RU' : 'en-US'; }

  window.I18N = { t, apply, setLang, onChange, plural, dateLocale, get lang() { return lang; } };

  document.documentElement.lang = lang;

  fetch('/api/settings', { cache: 'no-store' })
    .then(r => (r.ok ? r.json() : null))
    .then(s => { if (s && s.language && s.language !== lang) setLang(s.language); })
    .catch(() => {});
})();

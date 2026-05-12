# Гибридная система извлечения структурированной информации из договоров страхования

MVP веб-приложения для загрузки и просмотра договоров страхования в форматах DOCX и PDF.

На первом этапе приложение:

- принимает `.docx` и текстовые `.pdf`;
- сохраняет загруженный файл в папку `uploads`;
- записывает информацию о документе в SQLite;
- показывает историю загруженных документов;
- открывает страницу конкретного документа;
- извлекает обычный текст для предпросмотра, но не извлекает структурированные поля.

## Установка

Перейдите в папку проекта:

```bash
cd insurance_extractor
```

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте его в PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python run.py
```

После запуска откройте в браузере:

```text
http://127.0.0.1:5000
```

SQLite-база создается автоматически в папке `instance`.

## Тесты

```bash
pytest
```

## Debug DOCX parser

Чтобы быстро проверить извлеченный текст из конкретного DOCX-файла:

```bash
python debug_parse_docx.py uploads/example.docx
```

Скрипт печатает первые 2000 символов `ParsedDocument.full_text`.

## Debug PDF parser

Чтобы быстро проверить извлеченный текст из конкретного PDF-файла:

```bash
python debug_parse_pdf.py uploads/example.pdf
```

Скрипт печатает предупреждение, если текст не извлечен и PDF может быть сканом. OCR на этом этапе не используется.

## Структура проекта

```text
insurance_extractor/
  app/
    __init__.py
    models.py
    routes.py
    config.py
    services/
      docx_parser.py
      extraction_types.py
      pdf_parser.py
      text_normalizer.py
      regex_extractor.py
      validator.py
    templates/
      base.html
      index.html
      document.html
    static/
      css/style.css
      js/app.js
  uploads/
  instance/
  tests/
  pytest.ini
  debug_parse_docx.py
  debug_parse_pdf.py
  run.py
  requirements.txt
  README.md
```

## За что отвечают файлы

- `run.py` запускает Flask-приложение.
- `app/__init__.py` создает приложение, подключает базу данных и регистрирует маршруты.
- `app/config.py` хранит настройки: путь к базе, папку загрузок, лимит размера файла.
- `app/models.py` описывает таблицу `documents`.
- `app/routes.py` содержит обработчики страниц: главная, загрузка, просмотр документа.
- `app/services/docx_parser.py` читает текст из DOCX.
- `app/services/extraction_types.py` описывает dataclass-модели результата извлечения для JSON-ответов.
- `app/services/pdf_parser.py` читает текстовые PDF через `pdfplumber`, извлекает страницы, слова и координаты. OCR пока не подключен.
- `app/services/text_normalizer.py` приводит текст к более удобному виду.
- `app/services/regex_extractor.py` пока содержит заглушку для будущего извлечения полей.
- `app/services/validator.py` проверяет, что пользователь загрузил DOCX или PDF.
- `app/templates/` хранит HTML-шаблоны.
- `app/static/` хранит CSS и JavaScript.
- `uploads/` хранит загруженные DOCX- и PDF-файлы.
- `instance/` хранит SQLite-базу.
- `tests/` содержит базовые тесты.
- `pytest.ini` ограничивает запуск тестов папкой `tests`.

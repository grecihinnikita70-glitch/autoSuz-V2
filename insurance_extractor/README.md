# Гибридная система извлечения структурированной информации из договоров страхования

MVP веб-приложения для загрузки и просмотра договоров страхования в формате DOCX.

На первом этапе приложение:

- принимает только `.docx`;
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
- `app/services/text_normalizer.py` приводит текст к более удобному виду.
- `app/services/regex_extractor.py` пока содержит заглушку для будущего извлечения полей.
- `app/services/validator.py` проверяет, что пользователь загрузил DOCX.
- `app/templates/` хранит HTML-шаблоны.
- `app/static/` хранит CSS и JavaScript.
- `uploads/` хранит загруженные DOCX-файлы.
- `instance/` хранит SQLite-базу.
- `tests/` содержит базовые тесты.
- `pytest.ini` ограничивает запуск тестов папкой `tests`.

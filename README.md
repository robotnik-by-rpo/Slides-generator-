# Slide-deck-generator

## Описание
Slide-deck-generator — это инструмент командной строки для преподавателей, который превращает план занятия в черновик презентации. Модуль читает Markdown-план урока, структурирует его в слайды и конвертирует в PDF/PPTX/HTML с помощью Marp CLI.

Ключевая идея: Презентация становится производным результатом учебного плана, а не отдельным документом. Это сокращает время подготовки и обеспечивает согласованность материалов.

## Что умеет сейчас(MVP)
- Читает план занятия в формате Markdown
- Генерирует структуру слайдов с заголовками и тезисами
- Добавляет ссылки на исходные материалы
- Помечает места, требующие ручной доработки (TODO)
- Экспортирует в PDF, PPTX и HTML
- Отправляет сгенерированные файлы в Nextcloud
- Логирует события в LRS (xAPI-стейтменты)
- Поддерживает режим обновления существующих презентаций

## Быстрый старт
```bash
git clone <repository-url> slide-deck-generator

cd slide-deck-generator

make venv
make install
source .venv/bin/activate
```

На основе .env.example создать файл .env и добавить все необходимые токены
```bash 
cp .env.example .env
```
## Основные переменные
|Переменные|Описание|
|----------|--------|
|SLIDES_OUTPUT_FOLDER| Директория для сохранения результатов|
|THEME_MARP|Тема оформления слайдов|
|LRS_ENDPOINT|URL для отправки xAPI-стейтментов|
|API_NEXTCLOUD|URL Nextcloud для загрузки файлов|
|FOLDER_NEXTCLOUD|Папка в Nextcloud для сохранения|

## Использование

## Аргументы командный строки
|Аргумент|Описание|
|--------|--------|
|--plan|Путь к файлу плана занятия (.md)|
|--output|Директория для сохранения презентации (по умолчанию ./output)|
|--format|Формат экспорта: pdf, pptx, html, all|
|--update|Обновить презентации в указанной директории (должны быть .marp.md файлы)|

## Запуск с Docker
Для полноценного тестирования с LRS (Ralph) и Nextcloud:
```bash
make docker-build
make docker-up
```

Выполнение генерации внутри контейнера
```bash
docker exec slider-generator python -m src.slide_deck_generator --plan data/examples/simple.md --output /app/output/test --format all
```

Остановка
```bash
make docker-down
```

## Команды Makefile
|Команда|Описание|
|-------|--------|
|make install|Установка зависимостей|
|make venv|Установка виртуального окружения|
|make test|Запуск тестов|
|make test-conv|Процент покрытия тестов|
|make docker-build|Собрать контейнер модуля из образа|
|make docker-up|Поднять контейнеры с LRS, Nextcloud, модулем|
|make run-cli|Запуск cli (требует указания PLAN и OUTPUT)
 
.. Slide Deck Generator documentation master file, created by
   sphinx-quickstart on Wed Jul  1 00:32:18 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Slide Deck Generator documentation
==================================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.


Автоматическая генерация презентаций из Markdown с использованием AI.


Руководство пользователя
========================

Быстрый старт
-------------

.. code-block:: bash

   # Генерация презентации
   python -m src.__main__ --plan lesson.md --format pdf

   # Генерация всех форматов
   python -m src.__main__ --plan lesson.md --format all

   # Обновление существующей
   python -m src.__main__ --update ./output

Переменные окружения
--------------------

.. code-block:: bash

   # Обязательные
   API_AI=your_groq_api_key
   SLIDES_OUTPUT_FOLDER=/path/to/output
   LRS_ENDPOINT=http://localhost:8000/xAPI/statements
   API_NEXTCLOUD=http://localhost:8080

   # Опциональные
   THEME_MARP=default
   

Документация разработчика
=========================

Архитектура
-----------

Проект состоит из 4 основных модулей:

1. **parse** - Обработка Markdown и AI генерация
2. **generate** - Конвертация в PDF/PPTX/HTML
3. **metadata** - LRS и NextCloud интеграция
4. **cli** - Интерфейс командной строки

Установка для разработки
------------------------

.. code-block:: bash

   git clone <repo>
   cd slide_deck_generator
   make venv
   source venv/bin/activate
   make e
   make install

Запуск тестов
-------------

.. code-block:: bash

   pytest
   pytest --cov=src tests/


Модуль generate
---------------

.. automodule:: generate.generate
   :members:
   :undoc-members:

Модуль metadata
---------------

.. automodule:: metadata.metadata
   :members:
   :undoc-members:

Модуль parse
------------

.. automodule:: parse.parse
   :members:
   :undoc-members:

Модуль CLI
----------

.. automodule:: src.__main__
   :members:
   :undoc-members:

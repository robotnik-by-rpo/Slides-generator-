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

   # Токены приложения
   SLIDES_OUTPUT_FOLDER=Директория_для_сохранения_результатов
   THEME_MARP=Тема_оформления_слайдов_в_marp
   API_AI=API_LLM_модели_(в_коде_используются_запросы_к_API_Groq)

   # Токены для LRS 
   LRS_ENDPOINT=URL_для_отправки_xAPI-стейтментов
   LOGIN_LRS=Логин_для_индификации_в_LRS_платформе
   API_NEXTCLOUD=URL_Nextcloud_для_загрузки_файлов_в_docker_сети

   # Nextcloud
   FOLDER_NEXTCLOUD=Папка_в_Nextcloud_для_сохранения
   NEXTCLOUD_EXTERNAL_URL=URL_для_загрузки_файлов
   NEXTCLOUD_DB_HOST=Хост/адрес_сервера_PostgreSQL(имя_контейнера_с_postgreSQL_для_Nextcloud)
   NEXTCLOUD_DB=Имя_базы_данных,_которую_будет_использовать_Nextcloud
   NEXTCLOUD_USER=Имя_пользователя_для_подключения_к_PostgreSQL
   NEXTCLOUD_PASSWORD=Пароль_пользователя_PostgreSQL
   NEXTCLOUD_ADMIN_USER=Имя_администратора_Nextcloud 
   NEXTCLOUD_ADMIN_PASSWORD=Пароль_администратора_Nextcloud
   NEXTCLOUD_TRUSTED_DOMAINS=Доверенные_домены,_с_которых_можно_обращаться_к_Nextcloud_(например,_localhost,_your-domain.com)
   OVERWRITEPROTOCOL=Протокол_для_переопределения 
   OVERWRITEHOST=Хост_для_переопределения
   OVERWRITEWEBROOT=Корень_веб-приложения
   

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

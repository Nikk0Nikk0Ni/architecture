# ДЗ 02: REST API сервис

**Вариант 4 – Сайт заказа услуг (аналог https://profi.ru/)**

Архитектура платформы для заказа услуг (Микросервисы: User Service, Service Catalog, Order Service).
Реализовано на **Python + FastAPI** с in-memory хранилищем и JWT-аутентификацией.

## Запуск проекта

### Вариант 1: Через Docker 
1. Выполните команду в корне проекта:
   docker-compose up -d --build
2. API и документация будут доступны по адресу: http://localhost:8000/docs

### Вариант 2: Локально
1. Создайте виртуальное окружение: python -m venv venv
2. Активируйте его (Windows: venv\Scripts\activate, Mac/Linux: source venv/bin/activate)
3. Установите зависимости: pip install -r requirements.txt
4. Запустите сервер: uvicorn main:app --reload
5. Откройте в браузере: http://127.0.0.1:8000/docs

## Документация API

Интерактивная Swagger UI документация доступна из коробки.
Файл спецификации openapi.yaml сгенерирован и лежит в корне репозитория.

## Тестирование
В проекте написаны интеграционные тесты с использованием pytest и TestClient.
Для их запуска выполните команду в виртуальном окружении: pytest test_main.py -v
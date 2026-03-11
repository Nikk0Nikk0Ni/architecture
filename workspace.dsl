workspace {

    name "Сайт заказа услуг"
    description "Архитектура платформы для заказа услуг (Вариант 4) - Микросервисы"

    model {

        client = person "Клиент" "Пользователь, который ищет и заказывает услуги"
        specialist = person "Специалист" "Пользователь, который предоставляет услуги"

        emailSystem = softwareSystem "Email Сервис" "Внешняя система для отправки уведомлений"
        paymentSystem = softwareSystem "Платежная система" "Внешняя система для оплаты заказов"

        platform = softwareSystem "Платформа заказа услуг" {
            
            webApp = container "Web Application" "Интерфейс для работы клиентов и специалистов" "React / TypeScript"
            apiGateway = container "API Gateway" "Единая точка входа, маршрутизация запросов" "Nginx / Traefik"

            userService = container "User Service" "API: Создание пользователя, поиск по логину и ФИО" "Python / FastAPI"
            serviceCatalog = container "Service Catalog" "API: Создание услуги, получение списка услуг" "Python / FastAPI"
            orderService = container "Order Service" "API: Добавление услуги в заказ, получение заказа" "Python / FastAPI"

            database = container "Database" "Хранение пользователей, услуг и заказов" "PostgreSQL / YDB"
        }

        client -> platform "Поиск и заказ услуг"
        specialist -> platform "Управление своими услугами"

        platform -> emailSystem "Отправка уведомлений" "SMTP"
        platform -> paymentSystem "Инициация оплаты" "HTTPS/REST"

        client -> webApp "Использует интерфейс" "HTTPS"
        specialist -> webApp "Использует интерфейс" "HTTPS"

        webApp -> apiGateway "Отправляет API запросы" "HTTPS/JSON"

        apiGateway -> userService "Маршрутизирует запросы пользователей" "REST"
        apiGateway -> serviceCatalog "Маршрутизирует запросы услуг" "REST"
        apiGateway -> orderService "Маршрутизирует запросы заказов" "REST"

        userService -> database "Чтение/Запись данных пользователей" "SQL"
        serviceCatalog -> database "Чтение/Запись данных каталога" "SQL"
        orderService -> database "Чтение/Запись данных заказов" "SQL"

        orderService -> emailSystem "Отправка события для email-уведомления" "HTTPS/REST"
    }

    views {
        systemContext platform {
            title "System Context Diagram - Платформа заказа услуг"
            description "Система в контексте взаимодействия с пользователями и внешними сервисами."
            include *
            autoLayout
        }

        container platform {
            title "Container Diagram - Внутренняя архитектура платформы"
            description "Взаимодействие между микросервисами, фронтендом и базой данных."
            include *
            autoLayout
        }

        dynamic platform {
            title "Dynamic Diagram - Добавление услуги в заказ"
            description "Последовательность вызовов при добавлении выбранной услуги в заказ клиента."

            client -> webApp "Нажимает кнопку 'Добавить услугу в заказ'"
            webApp -> apiGateway "Отправление запроса на бек"
            apiGateway -> orderService "Перенаправление запроса в сервис заказов"
            
            orderService -> database "Сохранение связи услуги с заказом пользователя"
            database -> orderService "Подтверждение успешной записи"
            
            orderService -> emailSystem "Асинхронная отправка уведомления об изменении заказа"
            
            orderService -> apiGateway "Возврат успешного статуса ответа (200 OK)"
            apiGateway -> webApp "Передача ответа клиенту"
            webApp -> client "Обновление интерфейса (услуга в заказе)"

            autoLayout lr
        }

        themes default
    }
}
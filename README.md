# praktikum_new_diplom
# Продуктовый помощник Foodgram 

# Описание проекта Foodgram
«Продуктовый помощник»: приложение, на котором пользователи публикуют рецепты, 
подписываться на публикации других авторов и добавляють рецепты в избранное. 
Сервис «Список покупок» позволит пользователю создавать, а так же и скачать, список продуктов, 
которые нужно купить для приготовления выбранных блюд. 

# Запуск проекта в dev-режиме

- Клонируйте репозиторий с проектом на свой компьютер. В терминале из рабочей директории выполните команду:
    git clone https://github.com/Vladislav199912/foodgram-project-react

- Установить и активировать виртуальное окружение
    source /venv/bin/activate

- Установить зависимости из файла requirements.txt
    python -m pip install --upgrade pip
    pip install -r requirements.txt

- Создать файл .env в папке проекта:

    DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
    DB_NAME=postgres # имя базы данных
    POSTGRES_USER=postgres # логин для подключения к базе данных
    POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
    DB_HOST=db # название сервиса (контейнера)
    DB_PORT=5432 # порт для подключения к БД
    DEBUG=False

# Выполните миграции:

    python manage.py migrate


- В папке с файлом manage.py выполнить команду:
    python manage.py runserver

- Создание нового супер пользователя 
    python manage.py createsuperuser

# Загрузите статику:
    python manage.py collectstatic --no-input

# Заполните базу тестовыми данными: 
    python manage.py add_tags
    python manage.py add_ingidients


# Запуск проекта через Docker

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:

    git clone https://github.com/Vladislav199912/foodgram-project-react

- в Docker cоздаем образ :
    docker build -t foodgram .

Выполните команду:
    cd ../infra
    docker-compose up -d --build

# Выполните миграции:

    docker-compose exec backend python manage.py migrate

# Создайте суперпользователя:
    docker-compose exec backend python manage.py createsuperuser

# Загрузите статику:
    docker-compose exec backend python manage.py collectstatic --no-input

# Заполните базу тестовыми данными:
    docker-compose exec backend python manage.py add_tags
    docker-compose exec backend python manage.py add_ingidients 


# Автор:  
    Ермаков Владислав, https://github.com/Vladislav199912
# Данные для доступа:
    Login: 277122@mail.ru
    Password: Vladas182424
    domen: https://vfoodgrame.ddns.net/
    IP: 51.250.23.87
    PORT: 8080


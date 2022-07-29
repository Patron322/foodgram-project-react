# Проект Foodgram
Сайт Foodgram, «Продуктовый помощник».
Сервис для публикации рецептов. Пользователь может просматривать рецепты и скачивать лист ингридиентов для них.

[title](http://51.250.110.250)

### Технологии
- Python 3.7
- Django 3.2
 - Gunicorn
 - Nginx
 - Docker
 - PostgreSQL

# Запуск приложения на сервере
### 1. Клонируйте репозиторий проекта
```
git clone git@github.com:Patron322/foodgram-project-react.git
```
### 2. Перейдите в папку infra, создайте .env файл:

    DJANGO_DEBUG = False
    SECRET_KEY=THIS_SECRET_DJANGO_KEY
    ALLOWED_HOSTS=*
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432
   
### 3. В папке infra выполните команды:

- docker-compose up -d --build

- docker-compose exec backend python manage.py makemigrations

- docker-compose exec backend python manage.py migrate

- docker-compose exec backend python manage.py collectstatic --no-input

### По желанию можно наполнить базу данных:

- docker-compose exec backendb python manage.py loaddata fixtures.json

#### Админка:

- Логин: admin322
- email: a@a.ru
- Пароль: admin
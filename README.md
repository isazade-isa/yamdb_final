![Yamdb Workflow Status](https://github.com/isazade-isa/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)

## Проект YaMDb

### Описание:

Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
В каждой категории есть произведения: книги, фильмы или музыка.
Произведению может быть присвоен жанр (Genre) из списка предустановленных. Новые жанры может создавать только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы (Review) и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.
В репозитории в директории /data подготовлены несколько файлов .csv
Залить данные из файлов csv в базу данных можно импортировать данные средствами SQLite
нужную команду ищите здесь - https://sqlite.com/matrix/cli.html

### Технологии:

Python 3.7, Django 2.2.16, Django REST framework 3.12.4, JWT, Docker, CI/CD 

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:isazade-isa/yamdb_final.git
```

### Cоздать и активировать виртуальное окружение:

```
Для Mac  ---  python3 -m venv venv
Для Win  ---  python -m venv venv
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

### Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

### Переходим в папку с файлом docker-compose.yaml и поднимаем контейнеры (infra_db_1, infra_web_1, infra_nginx_1):

```
docker-compose up -d --build
```

### Выполняем миграции:

```
docker-compose exec web python manage.py makemigrations
```

```
docker-compose exec web python manage.py migrate
```

### Создаем суперпользователя:

```
docker-compose exec web python manage.py createsuperuser
```

### Собираем статику:

```
docker-compose exec web python manage.py collectstatic --no-input
```

### Создаем дамп базы данных:

```
docker-compose exec web python manage.py dumpdata > dumpPostrgeSQL.json
```

### Шаблон наполнения .env (не включен в текущий репозиторий) расположенный по пути infra/.env

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs
DEBUG_SECRET=False
ALLOWED_HOSTS=['*']
```

### Документация API YaMDb

```
Документация доступна по эндпойнту: http://localhost/redoc/
```

### Со-авторы проекта API YaMDb

```
https://github.com/isazade-isa
Разработал категории (Categories), жанры (Genres) и произведения (Titles): модели,
представления и эндпоинты к ним.

https://github.com/Babinich-Dev
Разработал отзывы (Review) и комментарии (Comments): модели, представления, эндпоинты,
права доступа к ним. А также рейтинги произведений.

https://github.com/emilheev
Разработал всю часть уплавления пользователями, регистрация и аутентификация,
работу с токеном, систему подтверждения через e-mail.
```

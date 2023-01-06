# Проект Продуктовый помощник FOODGRAM
![FOODGRAM, Продуктовый помощник](https://github.com/erges699/foodgram-project-react/actions/workflows/foodgram-project-react.yaml/badge.svg)

Проект создан в рамках обучения <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">Django</a> на факультете Бэкенд. Когорта №9+ Яндекс.Практикум.

Использованы следующие технологии и пакеты:
<p align="left"> 
<a href="https://www.python.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"> </a>
<a href="https://www.django-rest-framework.org/" target="_blank" rel="noreferrer"> <img src="https://www.django-rest-framework.org/img/logo.png" alt="django-rest-framework" width="80" height="40"> </a>
<a href="https://gunicorn.org/" target="_blank" rel="noreferrer"><img src="https://github.com/benoitc/gunicorn/blob/master/docs/logo/gunicorn.svg" alt="gunicorn" width="180" height="40"> </a>
</p>

- 🔭 requests
- 🔭 pytest-pythonpath
- 🔭 python-dotenv
- 🔭 asgiref
- 🔭 django-filter
- 🔭 djangorestframework-simplejwt
- 🔭 psycopg2-binary
- 🔭 PyJWT
- 🔭 pytz
- 🔭 sqlparse
- 🔭 reportlab

<h3 align="left">Описание:</h3>

Функционал проекта:

На сервисе Foodgram пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

<h3 align="left">Как запустить проект:</h3>

### Запустить терминал. По ssh подключиться к удаленному серверу:

```
$ ssh <username>@<host>
```

### Клонировать репозиторий и перейти в него:

```
git@github.com:erges699/foodgram-project-react.git
```

### Создать и активировать виртуальное окружение, установить в него зависимости:

```
$ python3 -m venv venv
$ . venv/bin/activate
$ python3 -m pip install --upgrade pip
$ pip install -r ./backend/foodgram/requirements.txt
$ pip install wheel
```

### В папке api_yamdb создайте файл .env с переменными окружения для работы с базой данных :

```
Пример:
DB_ENGINE = 'django.db.backends.postgresql'
DB_NAME = 'postgres'
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'postgres'
DB_HOST = 'db'
DB_PORT = '5432'
SECRET_KEY = '0123456789'
```

### В папке foodgram-project-react/infra/ создайте файл .env с переменными окружения для работы с базой данных:

```
Пример:
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

### Отправить файлы на удаленный сервер:

```
Отредактируйте файл nginx/default.conf и в строке server_name впишите IP виртуальной машины (сервера):
server_name 127.0.0.1 localserver your_remote_server_ip;

Запустите терминал на локальном копьютере. 
Скопируйте подготовленные файлы docker-compose.yaml и nginx/default.conf из вашего проекта на сервер:
scp docker-compose.yaml <username>@<host>:/home/<username>/docker-compose.yaml
scp default.conf <username>@<host>:/home/<username>/nginx/default.conf
```

### На удаленном сервере, перед запуском сборку контейнеров:
### Перейти в папку, содержащую docker-compose.yaml -> foodgram-project-react/infra:

```
$ systemctl status nginx
Остановить nginx, если он запущен:
$ systemctl stop nginx
```

```
Проверить, что нет запущенных контейнеров:
$ docker container ls

При необходимости остановить:
docker container stop <containerID>

Удалить контейнеры предыдущих неудачных попыток установки:
sudo docker-compose stop && sudo docker system prune -af
```

### Запустить сборку контейнеров:

```
sudo docker-compose up -d --build
```

### Если всё получилось, следующий шаг. Либо возврат к действиям по проверке и сборке контейнеров (выше):

```
Creating infra_db_1 ... done
Creating infra_backend_1 ... done
Creating infra_nginx_1 ... done
```

### Выполнить миграции и собрать статику:

```
sudo docker-compose exec django python manage.py makemigrations reviews
sudo docker-compose exec django python manage.py migrate --run-syncdb
sudo docker-compose exec django python manage.py collectstatic --no-input 
```
### Создать суперюзера:

```
sudo docker-compose exec django python manage.py createsuperuser

```

### Заполнение базы данных из csv файла

Для загрузки данных в пустую базу используйте в терминале команду 

```
docker-compose exec django manage.py import_ingredients
```

### Примеры запросов и ответов можно найти в документации API

http://84.201.162.198/api/docs/

### Админ-панель проекта:

http://84.201.162.198/admin/

```
login/password - admin/admin
email - admin@admin.com
```

<h3 align="left">Об авторе:</h3>
<a href="https://github.com/erges699" target="_blank">Сергей Баляба</a>

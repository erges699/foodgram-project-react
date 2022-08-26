# praktikum_foodgram-project-react
![FOODGRAM, Продуктовый помощник](https://github.com/erges699/foodgram-project-react/actions/workflows/foodgram-project-react.yml/badge.svg)

<h1 align="center">Привет! </h1>
<h3 align="center">Я студент факультета Бэкенд. Когорта №9+ Яндекс.Практикум</h3>
<h3 align="center"><a href="https://github.com/erges699" target="_blank">Сергей Баляба</a></h3>
<h3 align="center">Разрабатываю проект <a href="https://github.com/erges699/foodgram-project-react.git" target="_blank">FOODGRAM, Продуктовый помощник</a></h3>
<h3 align="left">В настоящее время изучаю <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">Django</a>, в проекте использую следующие фреймфорки: </h3>

- 🔭 requests
- 🔭 pytest-pythonpath
- 🔭 python-dotenv
- 🔭 asgiref
- 🔭 Django
- 🔭 django-filter
- 🔭 djangorestframework
- 🔭 djangorestframework-simplejwt
- 🔭 gunicorn
- 🔭 psycopg2-binary
- 🔭 PyJWT
- 🔭 pytz
- 🔭 sqlparse
- 🔭 reportlab

<h3 align="center">FOODGRAM, Продуктовый помощник. Описание:</h3>

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
sudo docker-compose exec backend python manage.py makemigrations reviews
sudo docker-compose exec backend python manage.py migrate --run-syncdb
sudo docker-compose exec backend python manage.py collectstatic --no-input 
```
### Создать суперюзера:

```
docker-compose exec backend python manage.py createsuperuser

```

### Заполнение базы данных из csv файла

Для загрузки данных в пустую базу используйте в терминале команду 

```
docker-compose exec backend manage.py import_ingredients
```

### Примеры запросов и ответов можно найти в документации API
### http://255.255.255.255/redoc/

from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import (Categorу, Comment, Genre, GenreTitle, Review,
                            Title, User)

ALREDY_LOADED_CATEGORY_ERROR_MESSAGE = """
Если необходимо снова загрузить данные CATEGORY из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""

ALREDY_LOADED_COMMENT_ERROR_MESSAGE = """
Если необходимо снова загрузить данные COMMENT из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""

ALREDY_LOADED_GENRE_ERROR_MESSAGE = """
Если необходимо снова загрузить данные COMMENT из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""

ALREDY_LOADED_GENRETITLE_ERROR_MESSAGE = """
Если необходимо снова загрузить данные COMMENT из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""

ALREDY_LOADED_REVIEW_ERROR_MESSAGE = """
Если необходимо снова загрузить данные COMMENT из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""

ALREDY_LOADED_TITLE_ERROR_MESSAGE = """
Если необходимо снова загрузить данные COMMENT из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""

ALREDY_LOADED_USER_ERROR_MESSAGE = """
Если необходимо снова загрузить данные COMMENT из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


def get_category():
    if Categorу.objects.exists():
        print('данные CATEGORY уже загружены')
        print(ALREDY_LOADED_CATEGORY_ERROR_MESSAGE)
        return
    print('Загружаю данные CATEGORY')
    for row in DictReader(
        open(
            f'{settings.BASE_DIR}/static/data/category.csv',
            'r',
            encoding="utf8"
        )
    ):
        category = Categorу(
            name=row['name'],
            slug=row['slug']
        )
        category.save()


def get_comment():
    if Comment.objects.exists():
        print('данные COMMENT уже загружены')
        print(ALREDY_LOADED_COMMENT_ERROR_MESSAGE)
        return
    print('Загружаю данные COMMENT')
    for row in DictReader(
        open(
            f'{settings.BASE_DIR}/static/data/comments.csv',
            'r',
            encoding="utf8"
        )
    ):
        review_obj = get_object_or_404(Review, pk=row['review_id'])
        author_obj = get_object_or_404(User, pk=row['author'])
        comment = Comment(
            id=row['id'],
            review=review_obj,
            text=row['text'],
            author=author_obj,
            pub_date=row['pub_date']
        )
        comment.save()


def get_genre():
    if Genre.objects.exists():
        print('данные GENRE уже загружены')
        print(ALREDY_LOADED_GENRE_ERROR_MESSAGE)
        return
    print('Загружаю данные GENRE')
    for row in DictReader(open(
            f'{settings.BASE_DIR}/static/data/genre.csv',
            'r',
            encoding="utf8"
    )):
        genre = Genre(
            name=row['name'],
            slug=row['slug']
        )
        genre.save()


def get_genretitle():
    if GenreTitle.objects.exists():
        print('данные GENRETITLE уже загружены')
        print(ALREDY_LOADED_GENRETITLE_ERROR_MESSAGE)
        return
    print('Загружаю данные GENRETITLE')
    for row in DictReader(
        open(
            f'{settings.BASE_DIR}/static/data/genre_title.csv',
            'r',
            encoding="utf8"
        )
    ):
        title_obj = get_object_or_404(Title, id=row['title_id'])
        genre_obj = get_object_or_404(Genre, id=row['genre_id'])
        genre_title = GenreTitle(
            id=row['id'],
            title=title_obj,
            genre=genre_obj
        )
        genre_title.save()


def get_review():
    if Review.objects.exists():
        print('данные уже REVIEW загружены')
        print(ALREDY_LOADED_REVIEW_ERROR_MESSAGE)
        return
    print('Загружаю данные REVIEW')
    try:
        for row in DictReader(open(
                f'{settings.BASE_DIR}/static/data/review.csv',
                'r',
                encoding="utf8"
        )):
            title_obj = get_object_or_404(Title, id=row['title_id'])
            author_obj = get_object_or_404(User, id=row['author'])
            review = Review(
                id=row['id'],
                title=title_obj,
                text=row['text'],
                author=author_obj,
                score=row['score'],
                pub_date=row['pub_date']
            )
            review.save()
    except Exception:
        pass


def get_title():
    if Title.objects.exists():
        print('данные уже TITLE загружены')
        print(ALREDY_LOADED_TITLE_ERROR_MESSAGE)
        return
    print('Загружаю данные TITLE')
    for row in DictReader(open(
            f'{settings.BASE_DIR}/static/data/titles.csv',
            'r',
            encoding="utf8"
    )):
        category_obj = get_object_or_404(Categorу, id=row['category'])
        title = Title(
            id=row['id'],
            name=row['name'],
            year=row['year'],
            category=category_obj
        )
        title.save()


def get_user():
    # if User.objects.exists():
    #   print('данные USER уже загружены')
    #   print(ALREDY_LOADED_USER_ERROR_MESSAGE)
    #   return
    print('Загружаю данные USER')
    for row in DictReader(open(
            f'{settings.BASE_DIR}/static/data/users.csv',
            'r',
            encoding="utf8"
    )):
        user = User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            role=row['role'],
            bio=row['bio'],
            first_name=row['first_name'],
            last_name=row['last_name']
        )
        user.save()


class Command(BaseCommand):
    help = "Загружает данные из *.csv"

    def handle(self, *args, **options):
        get_user()
        get_category()
        get_genre()
        get_title()
        get_review()
        get_comment()
        get_genretitle()

from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Tag

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из tags.csv"

    def handle(self, *args, **options):
        if Tag.objects.exists():
            print('данные уже загружены')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print('Загружаю данные')
        for row in DictReader(
                open(
                f'{settings.BASE_DIR}{settings.STATIC_URL}data/tags.csv',
                'r',
                encoding="utf8"
                ),
                fieldnames=("name", "color", "slug"),
                delimiter=','
             ):
            tag = Tag(
                name=row["name"],
                color=row["color"],
                slug=row["slug"]
            )
            tag.save()

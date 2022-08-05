from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из ingredient.csv"

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print('данные уже загружены')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print('Загружаю данные')
        for row in DictReader(
                open(
                './data/ingredients.csv',
                'r',
                encoding="utf8"            
                ),
                fieldnames=("name", "unit"),
                delimiter=','
            ):
            ingredient = Ingredient(
                name=row["name"],
                measurement_unit=row["unit"]
            )
            ingredient.save()

from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import User

ALREDY_LOADED_ERROR_MESSAGE = """
Если необходимо снова загрузить данные из CSV файлов,
сначала удалите файо db.sqlite3 для очистки базы данных.
Затем запустите `python manage.py migrate` для создания пустой
базы данных с таблицами"""


class Command(BaseCommand):
    help = "Загружает данные из tags.csv"

    def handle(self, *args, **options):
        # if User.objects.exists():
        #     print('данные уже загружены')
        #     print(ALREDY_LOADED_ERROR_MESSAGE)
        #     return
        print('Загружаю данные')
        for row in DictReader(
                open(
                f'{settings.BASE_DIR}{settings.STATIC_URL}data/users.csv',
                'r',
                encoding="utf8"
                ),
                fieldnames=(
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password"
                ),
                delimiter=','
        ):
            user = User(
                username=row["username"],
                email=row["email"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                password=row["password"]
            )
            user.save()

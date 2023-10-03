import csv

from django.core.management.base import BaseCommand

from django.conf import settings
from recipes.models import Tag

class Command(BaseCommand):
    """Команда для загрузки ингредиентов в базу данных """

    def handle(self, *args, **kwargs):
        with open(
                f'{settings.CSV_FILE_DIR}/tags.csv', encoding='utf-8'
        ) as file:
            csv_reader = csv.reader(file, delimiter=',', quotechar='"')
            for row in csv_reader:
                name = row[0]
                color = row[1]
                slug = row[2]
                Tag.objects.create(
                    name=name, color=color, slug=slug
                )
        print('Теги загружены')

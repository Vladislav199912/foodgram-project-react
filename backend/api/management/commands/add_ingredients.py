import csv
from recipes.models import Ingredient
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(
            f'{settings.CSV_FILE_DIR}/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            ingredients = (
                Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
                for row in reader
            )
            Ingredient.objects.bulk_create(ingredients)
        print(Ingredient.objects.count(),' ингредиентов загружено в БД')
         
import csv
import os

from django.core.management.base import BaseCommand
from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Выгружаем даннные ингредиентов из csv в базу.'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_name', default='ingredients.csv', nargs='?', type=str
        )

    def handle(self, *args, **options):
        with open(
            os.path.join(os.path.join(BASE_DIR, 'data'), options['file_name']),
            newline='',
            encoding='utf-8',
        ) as csvfile:
            items = csv.reader(csvfile, delimiter=',')
            for name, measurement_unit in items:
                ex = Ingredient.objects.filter(name=name).exists()
                if not ex:
                    Ingredient.objects.create(
                        name=name, measurement_unit=measurement_unit
                    )
        print('Данные успешно загружены!')

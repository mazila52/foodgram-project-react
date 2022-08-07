import csv

from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    help = 'Import csv ingredients'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, *args, **options):
        Ingredient.objects.all().delete()
        file_name = options['file_name']
        with open(file_name, 'r', encoding='utf-8') as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            ingredients = []
            for row in data:
                ingredient = Ingredient(name=row[0], measurement_unit=row[1])
                ingredients.append(ingredient)
                if len(ingredients) > 5000:
                    Ingredient.objects.bulk_create(ingredients)
                    ingredients = []
            if ingredients:
                Ingredient.objects.bulk_create(ingredients)

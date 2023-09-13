import csv
import io
from os.path import join
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class Command(BaseCommand):
    help = 'Import csv file with data for Ingredients using Django ORM'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        DATA_FOLDER = join(BASE_DIR, 'data')
        csvfile = io.open(join(DATA_FOLDER, 'ingredients.csv'),
                          encoding="utf-8")
        file = csv.reader(csvfile, delimiter=',')
        counter = 0
        for row in file:
            name = row[0]
            measurement_unit = row[1]
            obj, created = Ingredient.objects.get_or_create(
                name=name,
                measurement_unit=measurement_unit
            )
            if created:
                counter += 1
        print(counter, 'ingredients were added to database.')

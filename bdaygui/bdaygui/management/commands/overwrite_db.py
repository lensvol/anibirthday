# -*- coding: utf-8 -*-

import csv
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from bdaygui.models import Birthday, Importance


class Command(BaseCommand):
    help = 'Overwrite current DB state with data from CSV file'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('csv_file', type=str)

    def convert_to_record(self, csv_line):
        character_id, name, full_birthday, series, photo, is_important = csv_line

        name = name.decode('ascii', 'ignore')

        m = re.match('(\d+).(\d+).+', full_birthday)
        if not m:
            return

        day_of_birth, month_of_birth = m.groups()
        if day_of_birth == '??' or month_of_birth == '??':
            return

        if not character_id:
            character_id = 0

        importance_code = u"Нужно поздравлять" if is_important else u"Не нужно поздравлять"

        return Birthday(
            charid=character_id,
            name=name,
            day=day_of_birth,
            month=month_of_birth,
            series=series,
            photo=photo,
            importance=Importance.objects.get(name=importance_code)
        )


    def handle(self, *args, **options):
        connection.cursor()
        connection.connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")

        with open(options['csv_file'], 'r') as fp:
            reader = csv.reader(fp, delimiter=';')
            reader.next()

            for line, contents in enumerate(reader):
                record = self.convert_to_record(contents)
                if not record:
                    self.stdout.write('Malformed data at line #{0}, skipping...'.format(line))
                    continue

                existing_record = None
                updated = False

                existing_record, created = Birthday.objects.update_or_create(
                    name=record.name,
                    day=record.day,
                    month=record.month,
                    defaults={
                        'charid': record.charid,
                        'series': record.series,
                        'importance': record.importance,
                    },
                )

                info_tuple = (existing_record.pk, existing_record.name.encode('ascii', 'replace'), existing_record.charid)

                if not created:
                    self.stdout.write('Updated record {0}: {1} [#{2}]'.format(*info_tuple))
                else:
                    self.stdout.write('Create new record: {1} [#{2}]'.format(*info_tuple))
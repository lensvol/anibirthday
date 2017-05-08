#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import re
import sqlite3
from collections import namedtuple
import sys

Record = namedtuple('Record', ['name', 'day_of_birth',
                               'month_of_birth', 'series', 'photo_url', 'important'])


def new_record(csv_line):
    character_id, name, full_birthday, series, photo, is_important = csv_line

    m = re.match('(\d+).(\d+).+', full_birthday)
    if not m:
        return

    day_of_birth, month_of_birth = m.groups()
    if day_of_birth == '??' or month_of_birth == '??':
        return

    return Record(name, int(day_of_birth), int(month_of_birth), series, photo, bool(is_important))


if __name__ == '__main__':
    records = []

    with open(sys.argv[1], 'r') as fp:
        reader = csv.reader(fp, delimiter=';')
        reader.next()

        for line in reader:
            record = new_record(line)
            if record:
                records.append(record)

    conn = sqlite3.connect(sys.argv[2])
    conn.text_factory = str

    with conn:
        cursor = conn.cursor()

        cursor.execute(u"CREATE TABLE IF NOT EXISTS birthdays(name TEXT, day INTEGER, "
                       u"month INTEGER, series TEXT, original_name TEXT, photo TEXT, "
                       u"important BOOLEAN, PRIMARY KEY(name, day, month))")

        cursor.executemany(u"INSERT OR REPLACE INTO birthdays (name, day, month, series, photo, important) "
                           u"VALUES (?, ?, ?, ?, ?, ?)", records)

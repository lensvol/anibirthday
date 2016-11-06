#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import random
import sqlite3
import sys
import twitter
import yaml


DEFAULT_TEMPLATE = u'%(day)s %(month)s родился %(name)s из аниме %(series)s'
MONTHS = [
    u'января',
    u'февраля',
    u'марта',
    u'апреля',
    u'мая',
    u'июня',
    u'июля',
    u'августа',
    u'сентября',
    u'октября',
    u'ноября',
    u'декабря',
]


def load_cfg(fn=None):
    cfg = {}

    with open(fn or 'anibirthdays.yaml', 'r') as fp:
        cfg = yaml.safe_load(fp.read())
    return cfg


if __name__ == '__main__':
    if len(sys.argv) == 3:
        day = int(sys.argv[1])
        month = int(sys.argv[2])
    else:
        today = datetime.datetime.now()
        day = today.day
        month = today.month

    config = load_cfg()

    api = twitter.Api(
        consumer_key=config['twitter']['key'],
        consumer_secret=config['twitter']['secret'],
        access_token_key=config['twitter']['access_token']['key'],
        access_token_secret=config['twitter']['access_token']['secret'],
    )
    db = sqlite3.connect(config['db'])

    print 'Selecting characters with birthdays on %d/%d...' % (day, month)

    cursor = db.cursor()
    cursor.execute('SELECT name, original_name, series, photo FROM birthdays WHERE '
                   'day = ? AND month = ?', (day, month))
    records = cursor.fetchall()

    random.shuffle(records)

    max_tweets = config['twitter'].get('limit', 3)
    templates = config.get('templates', [DEFAULT_TEMPLATE])

    for name, original_name, series, photo in records[:max_tweets]:
        text = random.choice(templates) % {
                'day': day,
                'japanese': original_name,
                'month': MONTHS[month - 1],
                'name': name,
                'series': series,
            }
        api.PostUpdate(text, media=photo)

        print 'Congratulated %s!' % name

    print 'That\'s it!'

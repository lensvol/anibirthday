#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import random
import sqlite3
import sys
import traceback

import twitter
import yaml
from twitter import TwitterError

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


def prepare_hashtags(japanese_name):
    return [
        u'#%s生誕祭' % japanese_name,
        u'#%s生誕祭2017' % japanese_name,
    ]

def prepare_series_list(series):
    parts = series.split('\n')

    if len(parts) > 1:
        return ', '.join(parts[:-1]) + u' и ' + parts[-1]
    else:
        return parts[0]

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

    print 'Trying to select important characters...'
    cursor = db.cursor()
    cursor.execute('SELECT name, original_name, series, photo FROM birthdays WHERE '
                   'day = ? AND month = ? AND importance_id = 1', (day, month))
    records = cursor.fetchall()

    if not records:
        print 'Nobody important was found, so we are using regular schmucks...'
        cursor.execute('SELECT name, original_name, series, photo FROM birthdays WHERE '
                       'day = ? AND month = ?', (day, month))
        records = cursor.fetchall()

    random.shuffle(records)

    cursor.execute('SELECT template FROM tweet_templates')
    templates = cursor.fetchall()
    if not templates:
        templates = [DEFAULT_TEMPLATE]
    else:
        templates = map(lambda t: t[0], templates)

    max_tweets = config['twitter'].get('limit', 3)

    for name, original_name, series, photo in records[:max_tweets]:
        print 'Congratulating %s...' % name

        text = random.choice(templates) % {
                'day': day,
                'japanese': original_name,
                'month': MONTHS[month - 1],
                'name': name,
                'series': prepare_series_list(series),
            }

        hashtags = prepare_hashtags(original_name)
        for hashtag in hashtags:
            if len(text) + len(hashtag) + 1 <= 140:
                text += ' ' + hashtag

        if len(text) > 140:
            print 'Text too long: ', text
            continue
        else:
            try:
                api.PostUpdate(text, media=photo)
            except TwitterError:
                print traceback.format_exc()


    print '\nThat\'s it!\n'

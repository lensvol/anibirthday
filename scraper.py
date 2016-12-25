# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import copy
from random import shuffle, random
import requests
import re
import sys
import sqlite3
import time


LIST_CHARID_RE = re.compile('animedb.pl\?show=character&amp;charid=(\d+)')
PAGE_URL_TEMPLATE = 'https://anidb.net/perl-bin/animedb.pl?{}'
CHARACTER_PAGE_URI_TEMPLATE = 'show=character&charid={}'
MOCK_USER_AGENT = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)',
    'AppleWebKit/537.36 (KHTML, like Gecko)',
    'Chrome/51.0.2704.84 Safari/537.36',
]


def anidb_request(uri):
    complete_url = PAGE_URL_TEMPLATE.format(uri)
    return requests.get(
        complete_url,
        headers={
            'User-Agent': ' '.join(MOCK_USER_AGENT),
        }
    ).content


def get_character_page(character_id):
    return anidb_request(CHARACTER_PAGE_URI_TEMPLATE.format(character_id))



def extract_charids_from_list(raw_html):
    charids = LIST_CHARID_RE.findall(raw_html)
    return map(int, charids)


def extract_appearances(page):
    appearances = []
    appearance_table = page.find_all(
        'div',
        **{'class': 'pane anime_appearance'}
    )
    if appearance_table:
        names = appearance_table[0].find_all(
            'td',
            **{'class': 'name anime'}
        )
        appearances = [
            name.text
            for name in names
        ]

    return appearances


def get_character_photo_url(page):
    photo = page.find_all(
        'img',
        **{
            'itemprop': 'image',
            'class': 'g_image g_bubble',
        }
    )
    if photo:
        return photo[0].attrs['src']
    else:
        return ''


def get_character_properties(character_id):
    time.sleep(random())

    page = get_character_page(character_id)
    soup = BeautifulSoup(page, 'html.parser')
    data_table = soup.find_all('div', **{'class': 'g_definitionlist'})

    if not data_table:
        return

    properties = {
        'ID': character_id,
    }
    for row in data_table[0].find_all('tr'):
        field = row.find('th', **{'class': 'field'}).text
        value = row.find('td', **{'class': 'value'})

        inner_spans = value.find_all('span')
        if field == 'Official Name':
            value = value.find('label').text.strip()
        else:
            for span in inner_spans:
                if 'itemprop' in span.attrs or span.attrs.get('class') == 'tagname':
                    value = span.text
            else:
                if not isinstance(value, (unicode, str)):
                    value = value.text.strip()

        properties[field] = value

    appeared_in = '\n'.join(extract_appearances(soup))
    properties['Seen'] = appeared_in
    properties['Photo URL'] = get_character_photo_url(soup)

    return properties


def sorted_by_birthdate_character_list(page_num):
    return anidb_request('show=characterlist&page={}&orderby.birthdate=0.2&noalias=1'.format(page_num))


def list_characters(pages):
    for num in pages:
        page = sorted_by_birthdate_character_list(num)

        if 'do.unban.me' in page:
            sys.stdout.write('\a')
            sys.stdout.flush()
            print '!!! Please, open https://anidb.net/perl-bin/animedb.pl?show=characterlist and unban yourself. I\'ll wait.'
            confirmation = 'N'
            while confirmation != 'Y':
                confirmation = raw_input('[Y/N]')

            page = sorted_by_birthdate_character_list(num)

        if 'No results' in page:
            break

        charids = extract_charids_from_list(page)
        if not charids:
            break

        yield num, charids


if __name__ == '__main__':
    if len(sys.argv) == 3:
        character_list = list_characters(xrange(int(sys.argv[1]), int(sys.argv[2])))
    elif len(sys.argv) > 1:
        pages_to_download = map(int, sys.argv[1:])

        character_list = list_characters(pages_to_download)
    else:
        character_list = list_characters(xrange(0, 2048))

    all_characters = []
    total_changed_records = 0
    db = sqlite3.connect('birthdays.sqlite')
    cursor = db.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS birthdays(name TEXT, day INTEGER, "
                   "month INTEGER, series TEXT, original_name TEXT, photo TEXT, "
                   "important BOOLEAN, PRIMARY KEY(name, day, month))")

    try:
        for ind, ids in character_list:
            characters_with_birthdays = []
            print '\n[[[ Page {} ]]]\n'.format(ind)
            charids = list(set(copy.copy(ids)))
            shuffle(charids)

            for random_id in charids:
                # TODO: Skip ignored IDs read from file
                character_info = get_character_properties(random_id)
                if character_info and 'Date of Birth' in character_info:
                    try:
                        print '[{}] {}: '.format(
                            character_info['ID'],
                            character_info.get('Main Name', 'unknown'),
                        ),
                        print character_info['Date of Birth']
                    except UnicodeEncodeError:
                        pass

                    full_birthday = character_info.get('Date of Birth', 'unknown')
                    m = re.match('(\d+).(\d+).+', full_birthday)
                    if not m:
                        continue

                    day_of_birth, month_of_birth = m.groups()
                    if day_of_birth == '??' or month_of_birth == '??':
                        continue

                    # TODO: Insert only if records are missing
                    cursor.execute('INSERT OR REPLACE INTO birthdays (name, day, month, photo, series, original_name, important) '
                                   'values (?, ?, ?, ?, ?, ?, (SELECT important FROM birthdays WHERE name = ? and day = ?))',
                                   (character_info.get('Main Name', 'unknown'),
                                   day_of_birth, month_of_birth,
                                   character_info.get('Photo URL', 'unknown'),
                                   character_info.get('Seen', 'unknown'),
                                   character_info.get('Official Name', 'unknown'),
                                   character_info.get('Main Name', 'unknown'),
                                   day_of_birth))
                    total_changed_records += 1
                    db.commit()
                print '>>>', total_changed_records

    except Exception, e:
        print e
        pass

    columns = [
        'ID',
        'Main Name',
        'Official Name',
        'Date of Birth',
        'Seen',
        'Photo URL',
    ]

    print 'Saved %d records.' % total_changed_records

    db.close()

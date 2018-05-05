import requests
from bs4 import BeautifulSoup
from pymorphy2 import MorphAnalyzer
from collections import Counter
from re import split
from operator import itemgetter, attrgetter
from datetime import timedelta
import datetime


morph = MorphAnalyzer()


def isnoun(word):
    return 'NOUN' in word.tag.grammemes

def page_soup(content):
    return BeautifulSoup(content, 'html.parser')

def page_posts(content):
    return page_soup(content).find_all(class_='post post_preview')

def title_words(text):
    return [word for word in split('\W*', text) if word]

def title_nouns(title):
    return map(attrgetter('normal_form'), filter(isnoun, map(itemgetter(0), map(morph.parse, title_words(title)))))

def post_nouns(post):
    return title_nouns(post_title(post))

def post_title(post):
    return post.find(class_='post__title').text

def parse_date(text):
    monthMap = {
        'январь': 1,
        'февраль': 2,
        'март': 3,
        'апрель': 4,
        'май': 5,
        'июнь': 6,
        'июль': 7,
        'август': 8,
        'сентябрь': 9,
        'октябрь': 10,
        'ноябрь': 11,
        'декабрь': 12,
    }
    if 'сегодня' in text:
        return datetime.date.today() - timedelta(days=0)
    elif 'вчера' in text:
        return datetime.date.today() - timedelta(days=1)
    else:
        return datetime.date(
            datetime.date.today().year,
            monthMap[morph.parse(text.split(' ')[1])[0].normal_form],
            int(text.split(' ')[0]))

def post_date(post):
    return parse_date(post.find(class_='post__time').text.strip())

def post_week(post):
    return post_date(post).isocalendar()[1]

def week_range(week):
    first_day_of_year = datetime.datetime(2018, 1, 1)
    dow = first_day_of_year.isocalendar()[2]
    start_date = first_day_of_year - timedelta(dow) + timedelta((week-1) * 7)
    end_date = start_date + timedelta(6)
    return start_date, end_date

def get_title_noun_count_aggregated_by_week(root, limit):
    weeks = {}
    for i in range(1, limit+1):
        url = '{}/all/page{}/'.format(root, i)
        r = requests.get(url)
        for post in page_posts(r.text):
            try:
                weeknumber = post_week(post)
                weeks.setdefault(weeknumber, []).extend(post_nouns(post))

            except Exception as e:
                print('ERROR', type(e), str(e), 'url', url, 'post', post)
                continue

    for k, v in weeks.items():
        start_date, end_date= week_range(k)
        print('In {number}{numberth} week from {start_date} to {end_date} found {words}'.format(
            number=k, numberth={0: '??', 1: 'st', 2: 'nd'}.get(k, 'th'),
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            words=', '.join(map(itemgetter(0), Counter(v).most_common(3))))
        )


def analyze(root, limit):
    return get_title_noun_count_aggregated_by_week(root, limit)

import getopt, sys

def usage():
    print('''
usage: habranalyzer [--root] [--limit] [--help]

Habr analizer - an analyze tool, for WORDS of week.

Options:
  --help, -h
      Print this text.
  
  --root, -r
      Root address for page address forming, default is http://habr.com.
      
  --limit, -l
      Data items from the command line are serialized as form fields, default is 17.

Example:
    habranalyzer --root=http://habrahabr.com --limit=12 
        Analize first 12 pages from http://habrahabr.com 

''')

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hr:l:", ["help", "root=", "limit="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    root = 'http://habr.com'
    limit=17
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-r", "--root"):
            root = a
        elif o in ("-l", "--limit"):
            limit = int(a)
        else:
            assert False, "unhandled option"

    analyze(root, limit)

if __name__ == "__main__":
    main()
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

USER_AGENT = 'bluearchive-birthday-ical (+https://github.com/utgwkk/bluearchive-birthday-ical)'
SOURCE_URL = 'https://bluearchive.wikiru.jp/?SandBox/%E8%AA%95%E7%94%9F%E6%97%A5%E4%B8%80%E8%A6%A7'
SELECTOR = '#sortabletable1'

def fetch_wiki_html() -> str:
    resp = requests.get(SOURCE_URL, headers={'User-Agent': USER_AGENT})
    resp.raise_for_status()
    return resp.text

# [a, b, c, d, ... (even-sized)] -> [(a, b), (c, d), ...]
def pairwise(xs):
    snd = lambda x: x[1]
    evens = map(snd, filter(lambda x: x[0] % 2 == 0, enumerate(xs)))
    odds = map(snd, filter(lambda x: x[0] % 2 == 1, enumerate(xs)))
    for even, odd in zip(evens, odds):
        yield even, odd

def parse_birthday(birthday_str: str) -> datetime:
    parsed = datetime.strptime(birthday_str, '%m/%d')
    # XXX: 暫定的に2021年
    return parsed.replace(year=2021)

def main():
    html = fetch_wiki_html()
    soup = BeautifulSoup(html, features='html.parser')
    selected_tags = soup.select(SELECTOR)
    if len(selected_tags) == 0:
        raise RuntimeError(f'element for {SELECTOR} not found')

    table = selected_tags[0]
    tds = table.find_all('td')
    texts = [td.text for td in tds]
    parsed = pairwise(texts)

    print('''BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//utgwkk//Blue Archive Birthday Calendar//EN''')

    for name, birthday_str in parsed:
        birthday = parse_birthday(birthday_str)
        print('BEGIN:VEVENT')
        print(f'DTSTART;TZID=Asia/Tokyo:{birthday.strftime("%Y%m%dT%H%M%S")}')
        print(f'DTEND;TZID=Asia/Tokyo:{(birthday + timedelta(days=1)).strftime("%Y%m%dT%H%M%S")}')
        print('RRULE:FREQ=YEARLY;COUNT=100')
        print(f'SUMMARY:{name}')
        print('END:VEVENT')

    print('END:VCALENDAR')

if __name__ == '__main__':
    main()

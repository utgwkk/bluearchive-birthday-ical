from datetime import datetime, timedelta
from icalendar.prop import vFrequency
import re

import requests
from bs4 import BeautifulSoup
from icalendar.cal import Calendar, Event

USER_AGENT = 'bluearchive-birthday-ical (+https://github.com/utgwkk/bluearchive-birthday-ical)'
SOURCE_URL = 'https://bluearchive.wikiru.jp/?cmd=edit&page=MenuBar/%E8%AA%95%E7%94%9F%E6%97%A5%E4%B8%80%E8%A6%A7'
SELECTOR = 'textarea[name="original"]'

def fetch_wiki_html() -> str:
    resp = requests.get(SOURCE_URL, headers={'User-Agent': USER_AGENT})
    resp.raise_for_status()
    return resp.text

# [a, b, c, d, ... (even-sized)] -> [(a, b), (c, d), ...]
def pairs(xs):
    args = [iter(xs)] * 2
    return zip(*args)

def parse_birthday(birthday_str: str) -> datetime:
    parsed = datetime.strptime(birthday_str, '%m/%d')
    # XXX: 暫定的に2022年
    return parsed.replace(year=2022)

def main():
    html = fetch_wiki_html()
    soup = BeautifulSoup(html, features='html.parser')
    selected_tags = soup.select(SELECTOR)
    if len(selected_tags) == 0:
        raise RuntimeError(f'element for {SELECTOR} not found')

    parsed = []
    textarea = selected_tags[0]
    for line in textarea.text.splitlines():
        m = re.match(r'\|\s*\[\[(.+)\]\]\s*\|\s*([0-9]{2}/[0-9]{2})\s*\|', line)
        if not m:
            continue
        name = m.group(1)
        birthday = m.group(2)
        parsed.append((name, birthday))

    calendar = Calendar()
    calendar.add('prodid', '-//utgwkk//Blue Archive Birthday Calendar//JA')

    for name, birthday_str in parsed:
        birthday = parse_birthday(birthday_str)
        event = Event()
        event.add('summary', name)
        event.add('dtstart', birthday)
        event.add('dtend', birthday + timedelta(days=1))
        event.add('rrule', vFrequency('yearly'))
        calendar.add_component(event)

    print(calendar.to_ical().decode().strip())

if __name__ == '__main__':
    main()

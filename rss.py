from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from flask import Flask
import requests
from werkzeug.contrib.atom import AtomFeed

app = Flask(__name__)

MONTHS = [
        'ocak',
        'subat',
        'mart',
        'nisan',
        'mayis',
        'haziran',
        'temmuz',
        'agustos',
        'eylul',
        'ekim',
        'kasim',
        'aralik',
        ]

TEMPLATE = 'http://www.diken.com.tr/aksam-postasi-%s-%s-%s/'

def _get_url(date):
    month = MONTHS[date.month - 1]
    return TEMPLATE % (date.day, month, date.year)

def _get_item(date):
    """
    @param date: date
    @return: dict
    """
    url = _get_url(date)
    content = requests.get(url)
    soup = BeautifulSoup(content.text)
    headers = soup.find('div', {'class': 'entry-content'}).find_all('h4')
    month = MONTHS[date.month - 1]
    title = 'Aksam Postasi - %s %s %s' % (date.day, month, date.year)
    content = u''
    for header in headers:
        if not header.text:
            continue
        content += u"<h4>%s</h4>" % unicode(header.text)
        content += u"<p>%s</p>" % unicode(header.find_next_sibling().text)

    item = {
            'content_type': 'html',
            'url': url,
            'title': title,
            'content': content,
            'updated': date,
            'published': date,
            }
    return item

def get_feed(num_days, start_date=None):
    start_date = start_date or (datetime.now() - timedelta(days=1))
    feed = AtomFeed('Aksam Postasi - Diken Gazete',
                    feed_url='http://www.diken.com.tr/',
                    url='http://www.diken.com.tr/',
                    )
    for i in range(num_days):
        date = start_date - timedelta(days=i)
        item = _get_item(date)
        content = item['content']; del(item['content'])
        title = item['title']; del(item['title'])
        feed.add(title, content, **item)
    return feed

@app.route('/recent.atom')
def feed():
    return get_feed(3)

if __name__ == '__main__':
    app.run(
            host='0.0.0.0',
            debug=True,
            )
    #get_feed(3)

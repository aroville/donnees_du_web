import requests
from bs4 import BeautifulSoup
from tasktimer import call_repeatedly
import re
from pprint import pprint
import pandas as pd

FPO_URL = 'http://www.freepatentsonline.com/'
N = 10
links = []
visited = set()
REG = re.compile('(\/y\d{4})?\/?\d+\.html')
results_dict = []
html_info_titles = [
    'Title:',
    'Inventors:',
    'Publication Date:',
    'Assignee:'
]


def is_worth_visiting(href, urls):
    if href in visited:
        return False
    if href in urls:
        return False
    return REG.match(href) is not None


def get_from_fpo(urls):
    if not urls or len(visited) >= N:
        pd.DataFrame(results_dict).to_json('patents.json', orient='records')
        # pprint(results_dict)
        return True

    url = urls.pop(0)
    soup = BeautifulSoup(requests.get(FPO_URL + url).text, 'html.parser')

    patent_info = {}
    for div in soup.find_all('div', class_='disp_doc2'):
        title_div = div.find('div', class_='disp_elm_title')
        if title_div and title_div.string in html_info_titles:
            text = div.find('div', class_='disp_elm_text').text
            text = text.strip().replace('\n', '')
            text = ' '.join(text.split())
            patent_info[title_div.string] = text
    results_dict.append(patent_info)

    for l in soup.find_all('a', href=True):
        href = l.get('href')
        if not is_worth_visiting(href, urls):
            continue

        links.append(href)
        urls.append(href)

    visited.add(url)
    return False


if __name__ == '__main__':
    call_repeatedly(5, get_from_fpo, [
        '/y2015/0032669.html',
        '/y2003/0132591.html'
    ])

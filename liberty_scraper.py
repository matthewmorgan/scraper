import json

from bs4 import BeautifulSoup
from urllib import request


def scrape(url='http://digitalcommons.liberty.edu/honors/615/'):
    if not url.startswith('http://digitalcommons.liberty.edu/honors'):
        return
    print('Attempting to scrape url {}'.format(url))
    r = request.urlopen(url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")
    element_divs = soup.find_all('div', class_='element')

    results = {}

    title = soup.find('div', id='title').p.a
    results['title'] = title.text
    results['url'] = url
    
    for element in element_divs:
        key = element['id']
        print(key)
        if key != 'title':
            if key == 'authors':
                """
                authors block has [p], with p.strong.text = author name
                """
                ps = element.find_all('p')
                results[key] = [p.strong.text for p in ps if p]
            elif key == 'recommended_citation':
                results[key] = element.find('p').text.strip()
            elif key == 'bp_categories':  # disciplines
                disciplines = element.find('p').text.split('|')
                results[key] = [d.strip() for d in disciplines]
            elif key == 'keywords':
                disciplines = element.find('p').text.split(',')
                results[key] = [d.strip() for d in disciplines]
            else:
                if element.find('p'):
                    results[key] = element.find('p').text
                else:
                    results[key] = element.text

    return results

import json

from bs4 import BeautifulSoup
from urllib import request


scraped_urls = set()


def scrape(url='https://academiccommons.columbia.edu/catalog/ac:205534'):
    if url in scraped_urls:
        return []

    r = request.urlopen(url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")

    keys = soup.find_all('dt')

    results = {}

    title = soup.find('h1', itemprop='name')
    results['title'] = title.text

    for dt in keys:
        key = dt.text.strip()
        if key == 'Author(s):':
            """
            authors block has dd[span], with span.a.span.text = author name
            """
            spans = dt.find_next_sibling('dd').find_all('span')
            results[key] = [span.a.span.text for span in spans if span and span.a]
        elif key == 'Suggested Citation:':
            """
            citations block has dd[a].text = citation fragment, with commas separating
            """
            contents = dt.find_next_sibling('dd').contents
            results[key] = ''.join([content.string for content in contents if content])
        elif key == 'Subject(s):':
            spans = dt.find_next_sibling('dd').find_all('span', itemprop='keywords')
            results[key] = list(set([span.text for span in spans]))
        elif key == 'Department(s):':
            links = dt.find_next_sibling('dd').find_all('a')
            results[key] = [a.text for a in links]
        else:
            span = dt.find_next_sibling('dd').span
            results[key] = span.text if span else ''

    scraped_urls.add(url)
    return results

import json

from datetime import datetime

from bs4 import BeautifulSoup
from urllib import request

from scraper import scrape


def crawl(url='https://academiccommons.columbia.edu/catalog/browse/subjects'):
        return crawl_subjects(url)


# find all links below id in entry point, store in list
def crawl_subjects(url='https://academiccommons.columbia.edu/catalog/browse/subjects'):
    r = request.urlopen(url).read()
    soup = BeautifulSoup(r, "html.parser")

    links = soup.find('div', id='browse-box').find_all('a', href=True)

    print('At {url}, found {num} category links.'.format(url=url, num=len(links)))

    return links


def follow_subject_link(link, base_url='https://academiccommons.columbia.edu'):
    if not link:
        return []
    link_url = '{base_url}{link_href}'.format(base_url=base_url, link_href=link['href'])
    r = request.urlopen(link_url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")
    document_link_spans = soup.find_all('span', itemprop='url')

    return [span.a['href'] for span in document_link_spans]


def follow_document_link(link_url):
    if not link_url:
        return []
    return scrape(link_url)


def test_follow_link():
    return follow_document_link(link_url=follow_subject_link(link=crawl()[0])[0])

def test_follow_links(num=2):
    start = datetime.now()
    subject_links = crawl()[:num]
    results = []

    for subject_link in subject_links:
        document_links = follow_subject_link(subject_link)
        for document_link in document_links:
            results.append(follow_document_link(document_link))

    print('Processing {num} links took {time}.'.format(num=num, time=datetime.now() - start))
    print('Number of individual documents in results: {num_results}.'.format(num_results=len(results)))
    return results


def test_with_write(num=2):
    results = test_follow_links(num)
    with open('scraped_json.txt', 'w') as outfile:
        json.dump(results, outfile)

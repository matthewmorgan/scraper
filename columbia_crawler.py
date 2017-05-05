from datetime import datetime

from bs4 import BeautifulSoup
from urllib import request

from columbia_scraper import scrape
from columbia_mapper import map_json
from json_file_handler import copy_to_s3, write_to_local


def crawl(url='https://academiccommons.columbia.edu/catalog/browse/subjects'):
    return crawl_subjects(url)


def crawl_subjects(url='https://academiccommons.columbia.edu/catalog/browse/subjects'):
    r = request.urlopen(url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")
    links = soup.find('div', id='browse-box').find_all('a', href=True)

    print('At {url}, found {num} subject links.'.format(url=url, num=len(links)))
    return links

    
def follow_subject_link(link=None, base_url='https://academiccommons.columbia.edu', document_link_spans=None):
    if not link:
        return []
    link_url = '{base_url}{link_href}'.format(base_url=base_url, link_href=link['href'])
    print('following subject link {} {}'.format(link.text, link['href']))
    document_link_spans = document_link_spans or []
    try:
        r = request.urlopen(link_url, timeout=10).read()
        soup = BeautifulSoup(r, "html.parser")
        document_link_spans.extend(soup.find_all('span', itemprop='url'))

        next_page = soup.find('a', class_='next_page')

        if next_page:
            return follow_subject_link(link=next_page, document_link_spans=document_link_spans)

        print('-- scraping {num} document link(s)'.format(num=len(document_link_spans)))
        return [span.a['href'] for span in document_link_spans]
    except Exception as ex:
        print('Exception following subject link {}'.format(link_url))
        print(ex)
        return []


def follow_document_link(link_url):
    try:
        scraped_data = scrape(link_url) if link_url else []
    except Exception as ex:
        print('Exception following link {link}'.format(link=link_url))
        print(ex)
        return []
    return scraped_data


def follow_links():
    start = datetime.now()
    subject_links = crawl()
    results = []

    for subject_link in subject_links:
        document_links = follow_subject_link(subject_link)
        for document_link in document_links:
            results.append(follow_document_link(document_link))

    results = list(filter(lambda r: bool(r), results)) if results else []
    print('Processing {num} links took {time}.'.format(num=len(subject_links), time=datetime.now() - start))
    print('Number of individual documents in results: {num_results}.'.format(num_results=len(results)))
    return results


def crawl_with_write():
    results = follow_links()
    write_to_local(data=results, filename='unmapped_columbia_scraped_json.txt')
    mapped_results = [map_json(result) for result in results]
    write_to_local(data=mapped_results, filename='columbia_scraped_json.txt')
    copy_to_s3(filename='columbia_scraped_json.txt')

import json
import boto3

from datetime import datetime

from bs4 import BeautifulSoup
from urllib import request

from liberty_scraper import scrape
from liberty_mapper import map_json


subdiscipline_links = []


def crawl(url='http://digitalcommons.liberty.edu/do/discipline_browser/disciplines'):
    return list(set(crawl_page(url)))


def crawl_page(url, works_links=None):
    print('Crawling link {url}'.format(url=url))
    r = request.urlopen(url, timeout=30).read()
    soup = BeautifulSoup(r, "html.parser")
    subdiscipline_dd_tags = soup.find_all('dd', class_='sub-discipline')
    works_tags = soup.find_all('dd', class_='articles')

    works_links = works_links or []
    works_links.extend([works_tag.a['href'] for works_tag in works_tags])
    while subdiscipline_dd_tags:
        tag = subdiscipline_dd_tags.pop()
        crawl_page('http://digitalcommons.liberty.edu{}'.format(tag.a['href']), works_links)
    return works_links


def follow_discipline_link(link, base_url='http://digitalcommons.liberty.edu'):
    if not link:
        return []
    link_url = '{base_url}{link_href}'.format(base_url=base_url, link_href=link)
    print('trying to follow discipline link {link}: {link_url}'.format(link_url=link_url, link=link))
    r = request.urlopen(link_url, timeout=30).read()
    soup = BeautifulSoup(r, "html.parser")
    document_divs = soup.find_all('div', class_='entry')
    print('following discipline link {}'.format(link_url))
    print('-- scraping {num} document link(s)'.format(num=len(document_divs)))
    return [div.p.a['href'] for div in document_divs]


def follow_document_link(link_url):
    return scrape(link_url) if link_url else []


def copy_to_s3(bucket='ithaka-labs-data', filename='liberty_scraped_json.txt'):
    print('Copying local {filename} to s3 {bucket}'.format(filename=filename, bucket=bucket))
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=filename, Body=open(filename, 'rb'))


def write_to_local(results, filename='liberty_scraped_json.txt'):
    print('Writing results to local file {}'.format(filename))
    with open(filename, 'w') as outfile:
        json.dump(results, outfile)


def follow_links(num=1):
    start = datetime.now()
    works_links = crawl()
    print('Total number of works links found: {}'.format(len(works_links)))
    results = []

    for works_link in works_links:
        document_links = follow_discipline_link(works_link)
        for document_link in document_links:
            results.append(follow_document_link(document_link))

    print('Total results count before filtering out nulls: {}'.format(len(results)))
    results = list(filter(lambda r: bool(r), results)) if results else []

    print('Processing {num} discipline links took {time}.'.format(num=num, time=datetime.now() - start))
    print('Number of individual documents in results: {num_results}.'.format(num_results=len(results)))
    return results


def crawl_with_write(num=2):
    results = follow_links(num)
    mapped_results = [map_json(result) for result in results]
    write_to_local(mapped_results)
    copy_to_s3()

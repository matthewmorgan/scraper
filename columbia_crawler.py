import json
import boto3

from datetime import datetime

from bs4 import BeautifulSoup
from urllib import request

from columbia_scraper import scrape


def crawl(url='https://academiccommons.columbia.edu/catalog/browse/subjects'):
    return crawl_subjects(url)


def crawl_subjects(url='https://academiccommons.columbia.edu/catalog/browse/subjects'):
    r = request.urlopen(url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")
    links = soup.find('div', id='browse-box').find_all('a', href=True)

    print('At {url}, found {num} subject links.'.format(url=url, num=len(links)))
    return links


def follow_subject_link(link, base_url='https://academiccommons.columbia.edu'):
    if not link:
        return []
    link_url = '{base_url}{link_href}'.format(base_url=base_url, link_href=link['href'])
    r = request.urlopen(link_url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")
    document_link_spans = soup.find_all('span', itemprop='url')
    print('following subject link {}'.format(link.text))
    print('-- scraping {num} document link(s)'.format(num=len(document_link_spans)))
    return [span.a['href'] for span in document_link_spans]


def follow_document_link(link_url):
    return scrape(link_url) if link_url else []


def copy_to_s3(bucket='ithaka-labs-data', filename='columbia_scraped_json.txt'):
    print('Copying local {filename} to s3 {bucket}'.format(filename=filename, bucket=bucket))
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=filename, Body=open(filename, 'rb'))

    
def write_to_local(results, filename='columbia_scraped_json.txt'):
    print('Writing results to local file {}'.format(filename))
    results = results or []
    with open(filename, 'w') as outfile:
        json.dump(results, outfile)


def follow_links(num=1):
    start = datetime.now()
    subject_links = crawl()[:num]
    results = []

    for subject_link in subject_links:
        document_links = follow_subject_link(subject_link)
        for document_link in document_links:
            results.append(follow_document_link(document_link))

    results = list(filter(lambda r: bool(r), results)) if results else []
    print('Processing {num} links took {time}.'.format(num=num, time=datetime.now() - start))
    print('Number of individual documents in results: {num_results}.'.format(num_results=len(results)))
    return results


def crawl_with_write(num=2):
    results = follow_links(num)
    write_to_local(results)
    copy_to_s3()

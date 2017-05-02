import json
import boto3

from datetime import datetime

from bs4 import BeautifulSoup
from urllib import request

from liberty_scraper import scrape


def crawl(url='http://digitalcommons.liberty.edu/do/discipline_browser/disciplines'):
    return crawl_subjects(url)


def crawl_subjects(url='http://digitalcommons.liberty.edu/do/discipline_browser/disciplines'):
    r = request.urlopen(url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")
    dd_tags = soup.find('div', id='discipline-browser').find_all('dd', class_='articles')

    print('At {url}, found {num} discipline links.'.format(url=url, num=len(dd_tags)))
    return dd_tags


def extract_subject_link(dd_tag):
    return {
        'href': dd_tag.a['href']
    }


def follow_subject_link(link, base_url='http://digitalcommons.liberty.edu'):
    if not link:
        return []
    link_url = '{base_url}{link_href}'.format(base_url=base_url, link_href=link['href'])
    print('trying to follow subject link {}'.format(link_url))
    r = request.urlopen(link_url, timeout=10).read()
    soup = BeautifulSoup(r, "html.parser")
    document_divs = soup.find_all('div', class_='entry')
    print('following subject link {}'.format(link_url))
    print('-- scraping {num} document link(s)'.format(num=len(document_divs)))
    print(document_divs)
    return [div.p.a['href'] for div in document_divs]


def follow_document_link(link_url):
    return scrape(link_url) if link_url else []


def copy_to_s3(bucket='ithaka-labs-data', filename='liberty_scraped_json.txt'):
    print('Copying local {filename} to s3 {bucket}'.format(filename=filename, bucket=bucket))
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=filename, Body=open(filename, 'rb'))


def write_to_local(results, filename='liberty_scraped_json.txt'):
    print('Writing results to local file {}'.format(filename))
    results = list(filter(lambda r: r is not None, results)) if results else []
    with open(filename, 'w') as outfile:
        json.dump(results, outfile)


def follow_links(num=1):
    start = datetime.now()
    discipline_dd_tags = crawl()[:num]
    results = []

    for discipline_tag in discipline_dd_tags:
        document_links = follow_subject_link(extract_subject_link(discipline_tag))
        for document_link in document_links:
            results.append(follow_document_link(document_link))

    print('Processing {num} links took {time}.'.format(num=num, time=datetime.now() - start))
    print('Number of individual documents in results: {num_results}.'.format(num_results=len(results)))
    return results


def crawl_with_write(num=2):
    results = follow_links(num)
    write_to_local(results)
    # copy_to_s3()

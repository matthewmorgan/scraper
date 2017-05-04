from bs4 import BeautifulSoup
from urllib import request


def scrape(url='http://digitalcommons.liberty.edu/honors/615/'):
    print('Attempting to scrape url {}'.format(url))
    r = request.urlopen(url, timeout=30).read()
    soup = BeautifulSoup(r, "html.parser")

    # handle case of document not available
    if soup.find('p', class_='no-file'):
        print('!!! Endpoint contains no accessible document: {}'.format(url))
        return

    key_divs = soup.find('div', class_='work-details').find_all('div')

    results = {}

    title = soup.find('div', class_='work-details-title').text
    results['title'] = title

    partial_url_link = soup.find('div', class_='work-details-actions').find('div').find('div').find('a')
    if partial_url_link:
        results['url'] = 'https://works.bepress.com{}'.format(partial_url_link['href'])
    else:
        results['url'] = ''



    author_lis = soup.find('div', class_='authors').find('ul').find_all('li')
    results['authors'] = [author_li.span.text for author_li in author_lis]

    for key_div in key_divs:
        key_class = key_div['class']
        if key_class == ['abstract']:
            results['abstract'] = key_div.text
        if key_class == ['keywords']:
            keyword_lis = key_div.find('ul').find_all('li')
            results['keywords'] = [keyword_li.text for keyword_li in keyword_lis]
        if key_class == ['disciplines']:
            discipline_lis = key_div.find('ul').find_all('li')
            results['disciplines'] = [li.a.text for li in discipline_lis if li.a]
        if key_class == ['publication-date']:
            results['publication-date'] = key_div.find('div').next_sibling.strip()
        if key_class == ['citation']:
            results['citation'] = key_div.find('div', text='Citation Information').next_sibling.strip()

    return results

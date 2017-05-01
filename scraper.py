import json

from bs4 import BeautifulSoup
from urllib import request


def scrape(url='https://academiccommons.columbia.edu/catalog/ac:205534'):
    r = request.urlopen(url).read()
    soup = BeautifulSoup(r, "html.parser")

    dts = soup.find_all('dt')

    results_dict = {}

    for dt in dts:
        key = dt.text.strip()
        if (key == 'Author(s):'):
            """
            authors block has dd => span => a => span author name
            """
            spans = dt.find_next_sibling('dd').find_all('span')
            results_dict[key] = '; '.join([span.a.span.text for span in spans if span and span.a])
        elif (key == 'Suggested Citation:'):
            """
            citations block has dd => a
            """
            contents = dt.find_next_sibling('dd').contents
            results_dict[key] = ''.join([content.string for content in contents if content])
        else:
            span = dt.find_next_sibling('dd').span
            results_dict[key] = span.text if span else ''

    return json.dumps(results_dict)
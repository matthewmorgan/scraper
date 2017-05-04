from bs4 import BeautifulSoup
from urllib import request


from liberty_bepress_scraper import scrape as scrape_bepress


def scrape(url='http://digitalcommons.liberty.edu/honors/615/'):
    # only process endpoints we know how to scrape
    if url.startswith('https://works.bepress.com/'):
        return scrape_bepress(url)
    
    if not any([
                url.startswith('http://digitalcommons.liberty.edu/honors'),
                url.startswith('http://digitalcommons.liberty.edu/masters'),
                url.startswith('http://digitalcommons.liberty.edu/doctoral'),
                url.startswith('http://digitalcommons.liberty.edu/masters'),
                url.startswith('http://digitalcommons.liberty.edu/sob_lbr'),
                url.startswith('http://digitalcommons.liberty.edu/kabod'),
                url.startswith('http://digitalcommons.liberty.edu/honorable_mention'),
                url.startswith('http://digitalcommons.liberty.edu/cpe'),
                url.startswith('http://digitalcommons.liberty.edu/lujpr'),
                url.startswith('http://digitalcommons.liberty.edu/djrc'),
                url.startswith('http://digitalcommons.liberty.edu/sod_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/fidei_et_veritatis'),
                url.startswith('http://digitalcommons.liberty.edu/montview'),
                url.startswith('http://digitalcommons.liberty.edu/ljh'),
                url.startswith('http://digitalcommons.liberty.edu/jlbts'),
                url.startswith('http://digitalcommons.liberty.edu/eleu'),
                url.startswith('http://digitalcommons.liberty.edu/lujal'),
                url.startswith('http://digitalcommons.liberty.edu/educ_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/busi_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/health_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/lib_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/lusol_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/ccfs_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/psych_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/sor_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/cinema_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/fac_dis'),
                url.startswith('http://digitalcommons.liberty.edu/lts_grad_schol'),
                url.startswith('http://digitalcommons.liberty.edu/bio_chem_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/eml_undergrad_schol'),
                url.startswith('http://digitalcommons.liberty.edu/nurse_grad_fac_pubs'),
                url.startswith('http://digitalcommons.liberty.edu/nurse_grad_proj_schol'),
        ]
    ):
        print('!!! Unrecognized endpoint pattern {}'.format(url))
        return
    print('Attempting to scrape url {}'.format(url))
    r = request.urlopen(url, timeout=30).read()
    soup = BeautifulSoup(r, "html.parser")

    # handle case of document not available
    if soup.find('p', class_='no-file'):
        print('!!! Endpoint contains no accessible document: {}'.format(url))
        return

    element_divs = soup.find_all('div', class_='element')

    results = {}

    title_p = soup.find('div', id='title').p
    if title_p.a:
        results['title'] = title_p.a.text
        results['url'] = title_p.a['href']
    else:
        # handle case of external link in aside instead of title link
        results['title'] = title_p.text
        results['url'] = soup.find('a', id='remote-link')['href']

    
    for element in element_divs:
        key = element['id']
        if key != 'title':
            if key == 'authors':
                """
                authors block has [p], with p.strong.text = author name
                """
                ps = element.find_all('p')
                results[key] = [p.strong.text for p in ps if p and p.strong]
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

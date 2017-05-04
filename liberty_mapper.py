import dateparser


def map_json(raw):
    """
    Abstract:  abstract – string
    Advisors:  advisor – string array
    Authors:  author – string array
    Formatted citation:  citation - string
    Departments:  department – string array
    Disciplines: discipline – string array
    DOI:  doi – string
    Keywords:  keyword – string array
    Notes:  note – string array
    PDF URL:  pdf - string
    Publication date:  pubdate – ISO ‘YYYY-MM-DDZHH:MM:SSZ’ format        
    Publisher:  publisher - string
    Series:  series – string
    Source:  source - string literal (‘columbia’ or ‘liberty’)
    Stable URL:  stable_url - string
    Subjects:  subject – string array
    Title:  title – string
    Type:  type – string
    Year of publication:  year - integer
    """

    raw_date = raw.get('publication-date', raw.get('publication_date', ""))
    date_settings = {'TIMEZONE': 'UTC', 'PREFER_DAY_OF_MONTH': 'first', 'RETURN_AS_TIMEZONE_AWARE': True}
    publication_date = dateparser.parse(raw_date, settings=date_settings)

    keywords = raw.get('keywords', raw.get('bp_categories', []))
    disciplines = raw.get('disciplines', []) or raw.get('bp_categories', [])
    citation = raw.get('recommended_citation', raw.get('citation', ""))

    return {
        "abstract": raw.get('abstract', ""),
        "advisor": [],
        "author": raw.get('authors', []),
        "citation": citation,
        "department": raw.get('bp_categories', []),
        "discipline": disciplines,
        "doi": "",
        "keyword": keywords,
        "note": [],
        "pdf": raw.get('url', ""),
        "pubdate": publication_date.isoformat().replace('+00:00', 'Z'),
        "publisher": "",
        "series": "",
        "source": "liberty",
        "stable_url": raw.get('url', ""),
        "subject": raw.get('bp_categories', []),
        "title": raw.get('title', ""),
        "type": raw.get('document_type', ""),
        "year": publication_date.year
    }

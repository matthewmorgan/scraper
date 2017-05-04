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
    Publication date:  pubdate – ISO ‘YYYY-MM-DDZHH:MM:SSZ’ format        comment: We only have the year
    Publisher:  publisher - string
    Series:  series – string
    Source:  source - string literal (‘columbia’ or ‘liberty’)
    Stable URL:  stable_url - string
    Subjects:  subject – string array
    Title:  title – string
    Type:  type – string
    Year of publication:  year - integer
    """

    raw_date = raw.get('Date', "")
    date_settings = {'TIMEZONE': 'UTC', 'PREFER_DAY_OF_MONTH': 'first', 'RETURN_AS_TIMEZONE_AWARE': True}
    publication_date = dateparser.parse(raw_date, settings=date_settings).isoformat()
    publisher = raw.get('Suggested Citation', "")
    if publisher and len(publisher.split(', ')) >= 4:
        publisher = publisher.split(', ')[3]

    doi = raw.get('Persistent URL', "")
    if doi and doi.contains("hdl.handle.net/"):
        doi = doi.split("hdl.handle.net/")[1]

    return {
        "abstract": raw.get('Abstract', ""),
        "advisor": [],
        "author": raw.get('Author(s)', []),
        "citation": raw.get('Suggested Citation', ""),
        "department": raw.get('Departments', []),
        "discipline": raw.get('Subject(s)', []),
        "doi": doi,
        "keyword": raw.get('Subject(s)', []),
        "note": [],
        "pdf": raw.get('Persistent URL', ""),
        "pubdate": publication_date.__str__().replace('+00:00', 'Z'),
        "publisher":  publisher,
        "series": "",
        "source": "columbia",
        "stable_url": raw.get('Persistent URL', ""),
        "subject": raw.get('Subject(s)', []),
        "title": raw.get("Title", ""),
        "type": raw.get("Type", ""),
        "year": publication_date.year
    }

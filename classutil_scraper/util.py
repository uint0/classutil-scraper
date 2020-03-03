# -*- coding: utf-8 -*-
import unicodedata

def sanitize(s):
    """ Given a string, strips is and reencodes any format characters """
    return unicodedata.normalize("NFKD", s).strip()

def get_latest_update(html):
    """ Extracts the "latest update" field from a specialization_page """
    try:
        return sanitize(html.find('b').text)
    except:
        return sanitize(html.find('strong').text)

def get_row_values(row):
    """ Given a row of a table, extracts the text associated with each column """
    vals = []
    for col in row.find_all('td'):
        vals.append(sanitize(col.text))
    return tuple(vals)

def extract_table(tabl):
    for row in tabl.find_all('tr'):
        yield get_row_values(row)

def extract_links(html, parent_tag, parent_class):
    """ Given an index page, extract all the links found in <parent_tag>.<parent_class> """
    return [
        a.get('href')  # get the href of the anchor
        for a in filter(lambda x: x is not None, [  # for anchors that are in a <tag>.<class>
            col.find('a') for col in html.find_all(parent_tag, {'class': parent_class})
        ])
    ]

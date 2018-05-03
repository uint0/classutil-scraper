# -*- coding: utf-8 -*-

"""

scrape.py
=========
`python scrape.py <file>`

A python utility to scrape `http://classutil.unsw.edu.au/`
Data is stored a json format into a specified file.

"""

from Scraper import WebScraper
from Parsers import parsers
from util import extract_table, extract_links, get_latest_update
import json

BASE_URI = "http://classutil.unsw.edu.au/"

def normalize(scraped):
    """ Turns the return format from do_scrape into the schema type """
    normal = []
    for dat in scraped:
        url = dat['url']
        res = dat['res']

        spec, sess = url.split('.')[0].split('_')
        normal.append({
            "specialisation": spec,
            "session":        sess,
            "last_updated":   res['last_updated'],
            "courses":        res['courses']
        })
    return normal

def reformat_page(page):
    """ Reformats the enrollment and time to fit the schema """
    # matches  n/m [k] where k is optional

    for course in page:
        course["enrollment"] = {
            "status":         None,
            "capacity":       -1,
            "class_capacity": -1,
            "enrolled":       -1,
            "self_enrol":     True
        }

        for heading in tuple(course.keys()):
            if heading not in parsers:
                continue

            # 1. Get the associated structures
            parse_conf = parsers[heading]
            parser = parse_conf['parser']

            # 2. Run the parser, (making sure to only parse in args if it is non null)
            output = parser(course[heading], parse_conf['args'])

            # 3. Unpack the output into course
            out = parse_conf['out']
            key = None
            if isinstance(out, dict):
                key = tuple(out.keys())[0]
                out = tuple(out.values())[0]

            for i, v in enumerate(output):
                if key is None:
                    course[out[i]] = v
                else:
                    course[key][out[i]] = v

            # 4. Delete the heading
            del course[heading]

    return page

def parse_page(html, *args):
    """ Given the html of a specialisation page, extract the courses, and their associted data """

    rows = extract_table(html.find_all('table')[2])

    headings = tuple(map(lambda x: x.lower(), next(rows)))

    dat = []
    cur_dat = []
    cur_head = next(rows)  # preread the first course row

    for row in rows:
        # if the number of columns is 2 then we are on a course desc row
        if len(row) == 2:
            dat.append({
                "course":      cur_head[0],
                "description": cur_head[1],
                "classes":     reformat_page(cur_dat)
            })

            cur_dat = []
            cur_head = row
        else:
            cur_dat.append({headings[i]: val for i, val in enumerate(row)})

    return {
        "last_updated": get_latest_update(html),
        "courses":      dat
    }

def do_scrape(pages):
    """ Driver to call the get_batch method in scraper """
    return scraper.get_batch(pages,
                             page_hook=parse_page,
                             verbose=True)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: {} <file>".format(sys.argv[0]))
        exit(1)

    scraper = WebScraper(BASE_URI)
    latest_update = ""  # todo: something with this
    base = scraper.get_html()

    latest_update = get_latest_update(base)
    pages = extract_links(base, 'td', 'data')

    dat = do_scrape(pages)
    json.dump(normalize(dat), open(sys.argv[1], 'w'))

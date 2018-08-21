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


def ret_hook(res, url, out_buf, arg):
    """ A simple hook to save the result to a file before continuing """
    specialisation, sess = url.split('.')[0].split('_')

    for course in res['courses']:
        course_code = course['course']
        del course['course']
        arg[0].write('"{}": {}'.format(course_code, json.dumps(course)))
    # hacky concating to list in file
    if url != arg[1]:
        arg[0].write(',')
    arg[0].flush()


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
        elif len(row) == 1:
            # if the number of columns is 1, then we are at the bottom (i.e. reading ^ top ^)
            break
        else:
            cur_dat.append({ headings[i]: val for i, val in enumerate(row) })

    dat.append({
        "course":      cur_head[0],
        "description": cur_head[1],
        "classes":     reformat_page(cur_dat)
    })
    return {
        "last_updated": get_latest_update(html),
        "courses":      dat
    }


def do_scrape(pages, output):
    """ Driver to call the get_batch method in scraper """
    scraper.get_batch(pages,
                      page_hook=parse_page,
                      ret_hook=(ret_hook, [output, pages[-1]]),
                      verbose=True)


if __name__ == '__main__':
    import sys
    scraper = WebScraper(BASE_URI)

    try:
        output = open(sys.argv[1], 'w')
    except IndexError:
        print("Usage: {} <adaptors> <file>".format(sys.argv[0]))
        exit(1)

    output.write('{')

    latest_update = ""  # todo: something with this
    base = scraper.get_html()

    latest_update = get_latest_update(base)
    pages = extract_links(base, 'td', 'data')

    do_scrape(pages, output)

    output.write('}')

    output.close()

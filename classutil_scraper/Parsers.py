import re
from TimeFormat import TimeFormatService, parse_flag

CONSENT_TOK = '*'

class Headings:
    TIME     = "times (weeks, location) - default 1hour"
    STATUS   = "status"
    CAPACITY = "enr/cap"
    PFULL    = "% full"


def parse_times(time_string, *args):
    """ A driver to partition a full time string and call the Service on the partitions """
    parsed = []

    for time in time_string.split('; '):
        # 1. seperate out the bracketed (sessions) section
        tfs = TimeFormatService(time)

        if not tfs.is_empty():
            tfs.parse()
            parsed.append(tfs.as_dict())

    return (parsed,)


"""
enrol_re
--------
(\d{1,})      Group 1:    Capture 1 or more digit characters          (enrolled)
\/            NC:         Match '/' literal
(-?\d{1,})      Group 2:    Capture 1 or more digit characters          (capacity)
(?:\s\[       NC:       \ Match whitespace followed by a '[' literal
    (\d{1,})  Group 3:  | Capture 1 or more digit characters          (class_capacity)
\])           NC:       | Match a '[' literal 
?             Optional: /
"""
enrol_re = re.compile(r"(\d{1,})\/(-?\d{1,})(?:\s\[(\d{1,})\])?")
def parse_enrollment(enr_string, *args):
    found = list(enrol_re.findall(enr_string)[0])
    found[2] = found[1] if len(found[2]) == 0 else found[2]
    return tuple(map(int, found))


parsers = {
    Headings.TIME: {
        'parser': parse_times,
        'out':    ('times',),
        'args':   None
    },
    Headings.STATUS: {
        'parser': parse_flag,
        'out':    {'enrollment': ('self_enrol', 'status')},
        'args':   CONSENT_TOK
    },
    Headings.CAPACITY: {
        'parser': parse_enrollment,
        'out':    {'enrollment': ('enrolled', 'capacity', 'class_capacity')},
        'args':   None 
    },
    Headings.PFULL: {
        'parser': lambda x,y: [],
        'out':    (),
        'args':   None
    }
}


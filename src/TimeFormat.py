# -*- coding: utf-8 -*-
"""
Service to make the parsing of time strings and enrollments easier

Time String has format:
    [<day> <start>[-<end>][<cmod>]]
    [(w<wstart>[-<wend>]{,<wstart>[-<wend>][<mod>]}, <location>)]

Note: Basically the entire string is optional, so we need to be able to
      distinguish between cases where there is no prefix, and no suffix

Enrollment String is split accross two columns each with format:
   Enr/Cap: <enrolled>/<capacity>[ \[<class_capacity>\]]
   Status:  <status>[<emod>]

"""

import re
import json

def parse_flag(s, flag):
    has_flag = s[-1] == flag
    return (has_flag, s[:-1] if has_flag else s)


class TimeFormatService():
    """ A utility to support the formatting of the time field in a scraped page """
    FLAG_CLASH   = "#"

    WEEK_ALL  = 'all'
    WEEK_ODD  = 'odd'
    WEEK_EVEN = 'even'

    def __init__(self, timestr):
        self._parts = re.split(r"(\(.+\))", timestr)

        self.day       = None
        self.hours     = []
        self.clash     = False
        self.weeks     = []
        self.location  = None
        self.comb      = None 
        self.week_rule = TimeFormatService.WEEK_ALL

    @staticmethod
    def format_session(d):
        """ Given a array d [1, 2] or [1] it turns it into a dict with keys start, end """
        d = tuple(map(
                lambda x: int(x) if x.isdigit() else x,  # Try parsing to int
                filter(lambda x: len(x.strip()) > 0, d)  # Filter out empty strings
            ))

        end = d[0] if len(d) < 2 else d[1]
        return {'start': d[0], 'end': end}


    @staticmethod
    def is_time_sessions(s):
        """ Given a string, determine if it is in the format of a session """
        return s[0] == '(' and s[-1] == ')'

    @staticmethod
    def is_time_prefix(s):
        """ Given a string, determine if it is in the format of a prefix """
        days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        return s[:3] in days


    def extract_time_sessions(self, s):
        """ Given a string containing sessions data, extract it into the class """
        # 1. Strip off brackets
        s = s[1:-1]

        # 2. Split at ', ' to seperate into weeks, room
        parts = s.split(', ')

        # 3. Check the nature of the parts
        for part in parts:
            if len(part) == 0:
                continue
            # 3.1 if parts is length one, then we need to distinguish between the two
            if part[0] == 'w':
                # 3.1.1 if the first letter is 'w', then we are looking at weeks
                for p in part[1:].split(','):
                    self.weeks.append(TimeFormatService.format_session(p.split('-')))
            else:
                # 3.1.2 otherwise we are looking at the room
                self.location = part

    def extract_time_prefix(self, s):
        """ Given a string containing prefix data, extract it into the class """
        # 1. split it into day, hours
        parts = s.split(' ')

        # 2. Day is guaranteed to exist
        self.day = parts[0]

        # 3. Check if the hours exist
        if len(parts) > 1:
            hours = parts[1]
            # 3.1 Check the last character for the flag
            self.clash, hours = parse_flag(hours, TimeFormatService.FLAG_CLASH)

            # 3.1 add the hours
            self.hours = TimeFormatService.format_session(hours.split('-'))

    def extract_time_suffix(self, s):
        """ Given a string containing suffix data, extract it into the class """
        # 1. Determine the nature of the part
        if s[0] == '/':
            # 1.1 if the first charater is slash, we are determining the week_rule
            self.week_rule = TimeFormatService.WEEK_ODD if s[1:] == "odd" else TimeFormatService.WEEK_EVEN
        else:
            # 1.2 otherwise we have a comb rule
            self.comb = s.split(' ', 1)[1]

    def parse(self):
        """ Driver function to route and perform parseing """
        for part in self._parts:
            if len(part) == 0:
                continue

            if TimeFormatService.is_time_sessions(part):
                self.extract_time_sessions(part)
            elif TimeFormatService.is_time_prefix(part):
                self.extract_time_prefix(part)
            else:
                self.extract_time_suffix(part)

    def is_empty(self):
        """ Returns whether or not the current parts has any content """
        return len(self._parts) == 0

    def as_dict(self):
        """ Returns a dict representation of the key fields in the class """
        return {
            "day":       self.day,
            "hours":     self.hours,
            "clash":     self.clash,
            "weeks":     self.weeks,
            "location":  self.location,
            "comb":      self.comb,
            "week_rule": self.week_rule
        }

    def as_json(self):
        """ Returns a json string representation of the kye fields in the class """
        return json.dumps(self.as_dict())


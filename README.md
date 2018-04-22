# classutil-scraper
A python scraper for http://classutil.unsw.edu.au/

Setup
---
The scraper can be setup with the requirements.txt

```bash
pip3 install -r requirements.txt
```

Usage
---
The scraper can be invoked with python and takes one argument - the file to output to

```bash
python scrape.py <output file>
```

Output Schema
---
```json

[
    {
        "course":      string,
        "description": string
        "data": [
            {
                "comp":       string,
                "sect":       string,
                "class":      string,
                "type":       string,
                "enrolement": [
                    "status":         'Open' | 'Tent' | 'Full' | 'Closed' | 'Stop' | 'Canc',
                    "capacity":       int,
                    "class_capacity": int,
                    "enrolled":       int,
                    "self_enrol":     boolean=true
                ],
                "times": [
                    {
                        "day":   string | null,
                        "hours": {"start": int, "end": int} | null,
                        "weeks": [
                            {"start": int | string, "end": int | string},
                            ...
                        ],
                        "location":  string | null,
                        "clash":     boolean,
                        "combined":  string | null,
                        "week_rule": 'all' | 'odd' | 'even'
                    },
                    ...
                ]
            },
            ...
        ]
    },
    ...
]


```

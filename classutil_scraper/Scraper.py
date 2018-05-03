# -*- coding: utf-8 -*-

import requests
import bs4

def unpack_hook(hook):
    """ Unpacks a hook into a callback and a argument if it is a tuple """
    if isinstance(hook, tuple) and len(hook) > 1:
        return hook
    return (hook, None) 

def default_ret_hook(cbk_res, url, out, r):
    """ A default hook to append to a output buffer """
    out.append({
        "url": url,
        "res": cbk_res
    })

class WebScraper:
    """ A small class to help with web scraping """

    def __init__(self, base=None):
        self._sess = requests.Session()
        self._base = "" if base is None else base + ("/" if base[-1] != "/" else "")
        self._last = ""

    def get_html(self, url="", **kwargs):
        """ Gets the content of a webpage (relative to the base), and attempts to parse it to html """
        self._last = self._sess.get("{}{}".format(self._base, url), **kwargs)
        return bs4.BeautifulSoup(self._last.text, "html.parser") if self._last.status_code // 100 == 2 else None

    def get_batch(self, urls, page_hook, ret_hook=default_ret_hook, verbose=False, **kwargs):
        """ Given a list of urls, actuates on all of them """
        page_hook, page_args = unpack_hook(page_hook)
        ret_hook,  ret_args  = unpack_hook(ret_hook)

        ret = [] 
        for url in urls:
            if verbose: print(url)
            ret_hook(page_hook(self.get_html(url, **kwargs), page_args), url, ret, ret_args)

        return ret


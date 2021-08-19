from __future__ import annotations
import requests
import re
import typing as T
import warnings
import urllib3
import logging
from pathlib import Path
from . import files

TIMEOUT = 3
RETRYCODES = (400, 404, 405, 503)
# multiple exceptions must be tuples, not lists in general
OKE = requests.exceptions.TooManyRedirects  # FIXME: until full browswer like Arsenic implemented
EXC = (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError)

"""
synchronous routines
"""

def check_urls(
    urls: list[ dict ],
    hdr: dict[str, str] = None,
    verifycert: bool = False
) -> list[tuple[str, str, T.Any]]:

    bads: list[tuple[str, str, T.Any]] = []
    warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
    missing = []
    
    with requests.Session() as sess:
        if hdr:
            sess.headers.update(hdr)
            sess.max_redirects = 5
            
        # %% loop
        for u in urls:
            url = u['url']
            try:
                R = sess.head(url, allow_redirects=True, timeout=TIMEOUT, verify=verifycert)
                if R.status_code in RETRYCODES:
                    if retry(url, hdr, verifycert):
                        continue
                    else:
                        #yield u, url, R.status_code
                        missing.append( [ u['fn'], u['url'], R.status_code ] )
                        continue
            except OKE:
                continue
            except EXC as e:
                if retry(url, hdr, verifycert):
                    continue
                missing.append( [ u['fn'], u['url'], str(e) ] )
                #yield u, url, str(e)
                continue

            code = R.status_code
            if code != 200:
                #yield u, url, code
                missing.append( [ u['fn'], u['url'], code ] )
                logging.info(f'NOT FOUND: {url:80s}')
            else:
                logging.info(f"OK: {url:80s}")
                
    return missing
            
def retry(url: str, hdr: dict[str, str] = None, verifycert: bool = False) -> bool:
    ok = False
    try:
        # anti-crawling behavior doesn't like .head() method--.get() is slower but avoids lots of false positives
        with requests.get(
            url, allow_redirects=True, timeout=TIMEOUT, verify=verifycert, headers=hdr, stream=True
        ) as stream:
            Rb = next(stream.iter_lines(80), None)
            # if Rb is not None and 'html' in Rb.decode('utf8'):
            if Rb and len(Rb) > 10:
                ok = True
    except EXC:
        pass

    return ok

#!/usr/bin/env python

import sys
import pdoc

def df(doc_object):
    for module in WHITELISTED_MODULES:
        if module in doc_object.refname:
            return True
    return False

WHITELISTED_MODULES = sys.argv[1:]

html = pdoc.html('concrete', docfilter=df)
print html

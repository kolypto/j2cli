#! /usr/bin/env python

import json
import inspect
from exdoc import doc, getmembers

import shinto_cli
import shinto_cli.context
import shinto_cli.extras.filters


README = {
    'formats': {
        name: doc(f)
        for name, f in shinto_cli.context.FORMATS.items()
    },
    'extras': {
        'filters': [doc(v)
                    for k, v in getmembers(shinto_cli.extras.filters)
                    if inspect.isfunction(v)]
    }
}

print json.dumps(README)

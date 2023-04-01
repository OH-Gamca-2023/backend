import os
from functools import reduce

import yaml

lang_file = "lang.yml"
lang = yaml.load(open(lang_file, "r"), Loader=yaml.FullLoader)


def get_message(key, reloaded = False):
    global lang
    try:
        return reduce(lambda d, k: d[k], key.split("."), lang)
    except KeyError:
        if os.environ.get("ENVIRONMENT") == "dev" and not reloaded:
            lang = yaml.load(open(lang_file, "r"), Loader=yaml.FullLoader)
            return get_message(key)
        else:
            return key

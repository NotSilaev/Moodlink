import re


def escape_string(value):
    return re.sub(r'(["\\])', r'\\\1', value)
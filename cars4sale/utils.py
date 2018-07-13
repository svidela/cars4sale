import unicodedata
import re
import urllib

currency_mappings = {
    '$'    : 'ARS',
    'ARS'  : 'ARS',
    'USD $': 'USD',
    'U$S'  : 'USD',
    'USD'  : 'USD'
}

def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

def drop_dot(value):
    return value.replace('.','')

def split_and_get(value, at=0):
    return value.split()[at]

def dash_to_space(value):
    return value.replace('-', ' ')

def drop_last_word(value):
    return ' '.join(value.split()[:-1])

def drop_url_query(value):
    url = urllib.parse.urlparse(value)
    return url.scheme + '://' + url.netloc + url.path

def to_int(value):
    if value.isdigit():
        return int(value)

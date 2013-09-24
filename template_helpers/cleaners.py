import bleach


attrs = {
    '*': ['style']
}
tags = ['p', 'em', 'strong']
styles = ['color', 'font-weight']


def clean(text):
    return bleach.clean(text, tags, attrs, styles, strip=True)
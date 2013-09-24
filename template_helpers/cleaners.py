import bleach


attrs = {
    '*': ['style']
}
tags = ['p', 'em', 'strong', 'ul', 'li', 's', 'h1', 'h2', 'h3', 'div', 'ol', 'pre']
styles = ['color', 'font-weight', 'font-style', 'color', 'background', 'border', 'padding']


def clean(text):
    return bleach.clean(text, tags, attrs, styles, strip=True)
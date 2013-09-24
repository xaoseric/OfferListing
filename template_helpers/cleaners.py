import bleach


def clean(text):
    attrs = {
        '*': ['style']
    }
    tags = ['p', 'em', 'strong', 'ul', 'li', 's', 'h1', 'h2', 'h3', 'div', 'ol', 'pre']
    styles = ['color', 'font-weight', 'font-style', 'color', 'background', 'border', 'padding']
    return bleach.clean(text, tags, attrs, styles, strip=True)


def super_clean(text):
    attrs = {
        '*': ['style']
    }
    tags = ['p', 'em', 'strong', 'ul', 'li', 's', 'ol']
    styles = ['color', 'font-weight']
    return bleach.clean(text, tags, attrs, styles, strip=True)

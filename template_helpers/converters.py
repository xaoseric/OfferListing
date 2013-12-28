from markdown import Markdown

markdown_converter = Markdown(extensions=[
    # Extensions
    'abbr',
    'attr_list',
    'def_list',
    'fenced_code',
    'tables',
    'smart_strong',
    # Others
    'codehilite',
    'nl2br'
], safe_mode="escape")

from markdown import Markdown

markdown_converter = Markdown(extensions=['extra', 'codehilite', 'nl2br'], safe_mode="escape")

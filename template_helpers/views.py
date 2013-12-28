from django.views.generic import View
from braces.views import JSONResponseMixin, CsrfExemptMixin
from template_helpers.converters import markdown_converter


class MarkdownToHtmlView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):

        return_html = {
            "html": None,
            "error": None
        }

        if "markdown" not in request.POST:
            return_html["error"] = "No markdown sent!"
        else:
            markdown = request.POST["markdown"]
            return_html["html"] = markdown_converter.convert(markdown)

        return self.render_json_response(return_html)

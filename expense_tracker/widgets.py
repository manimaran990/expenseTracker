from django.forms.widgets import TextInput
from django.utils.html import format_html

class TextInputWithDatalist(TextInput):
    def __init__(self, datalist, *args, **kwargs):
        self.datalist = datalist
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        datalist_html = '<datalist id="datalist-{name}">{options}</datalist>'.format(
            name=name,
            options=''.join('<option value="%s">%s</option>' % (option.pk, option) for option in self.datalist)
        )
        text_input_html = super().render(name, value, attrs, renderer)
        return format_html('{}{}', text_input_html, datalist_html)

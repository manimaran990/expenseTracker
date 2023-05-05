from django.db import models
import uuid

class AutoUUIDField(models.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = uuid.uuid4
        kwargs['editable'] = False
        super().__init__(*args, **kwargs)

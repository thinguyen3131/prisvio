from rest_framework import serializers


class ImageFieldWithDefaultURLRepr(serializers.ImageField):
    def __init__(self, default_url_repr=None, *args, **kwargs):
        self.default_url_repr = default_url_repr
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if not value:
            request = self.context.get('request', None)
            if request is not None:
                return request.build_absolute_uri(self.default_url_repr)
        return super().to_representation(value)
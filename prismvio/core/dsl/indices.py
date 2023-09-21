from copy import deepcopy

from django.conf import settings
from elasticsearch_dsl import Index as DSLIndex

from .registries import registry


class Index(DSLIndex):
    @classmethod
    def default_index_settings(cls):
        return getattr(settings, "ELASTICSEARCH_DSL_INDEX_SETTINGS", {})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_index_settings = deepcopy(self.default_index_settings())
        self.settings(**default_index_settings)

    def document(self, document):
        """
        Extend to register the document in the global document registry
        """
        document = super().document(document)
        registry.register_document(document)
        return document

    doc_type = document

    def __str__(self):
        return self._name

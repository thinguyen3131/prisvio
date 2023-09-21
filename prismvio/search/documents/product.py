from prismvio.core.dsl import fields
from prismvio.core.dsl.documents import Document
from prismvio.core.dsl.registries import registry
from prismvio.menu_merchant.models import Products


@registry.register_document
class ProductsDocument(Document):
    hashtag = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
        }
    )
    keyword = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
        }
    )
    category = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name_vi": fields.TextField(),
            "name_en": fields.TextField(),
        }
    )

    class Index:
        name = "products"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Products
        fields = [
            "name",
            "description",
            "created_at",
            "updated_at",
        ]

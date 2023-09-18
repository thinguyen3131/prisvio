from django.contrib.auth import get_user_model
from elasticsearch_dsl import analyzer

from prismvio.core.dsl import fields
from prismvio.core.dsl.documents import Document
from prismvio.core.dsl.registries import registry
from prismvio.menu_merchant.models import Hashtag, Keyword
from prismvio.merchant.models import Merchant

User = get_user_model()


html_strip = analyzer(
    'html_strip',
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


# @registry.register_document
# class UserDocument(Document):
#     class Index:
#         name = "users"
#         settings = {
#             "number_of_shards": 1,
#             "number_of_replicas": 0,
#         }
#
#     class Django:
#         model = User
#         fields = [
#             "id",
#             "first_name",
#             "last_name",
#             "username",
#             "email",
#             "phone_number",
#         ]
#
#
# @registry.register_document
# class CategoryDocument(Document):
#     id = fields.IntegerField()
#
#     class Index:
#         name = "categories"
#         settings = {
#             "number_of_shards": 1,
#             "number_of_replicas": 0,
#         }
#
#     class Django:
#         model = Category
#         fields = [
#             "name_vi",
#             "name_en",
#             "notes",
#         ]


# @registry.register_document
# class HashtagDocument(Document):
#     id = fields.IntegerField()
#
#     class Index:
#         name = "hastags"
#         settings = {
#             "number_of_shards": 1,
#             "number_of_replicas": 0,
#         }
#
#     class Django:
#         model = Hashtag
#         fields = [
#             "id",
#             "name",
#         ]
#
#
# @registry.register_document
# class KeywordDocument(Document):
#     id = fields.IntegerField()
#
#     class Index:
#         name = "keywords"
#         settings = {
#             "number_of_shards": 1,
#             "number_of_replicas": 0,
#         }
#
#     class Django:
#         model = Keyword
#         fields = [
#             "id",
#             "name",
#         ]


@registry.register_document
class MerchantDocument(Document):
    normalizer_name = fields.TextField(attr="normalizer_name")

    description = fields.TextField(
        analyzer=html_strip,
        fields={'raw': fields.KeywordField()}
    )

    hashtags = fields.ListField(fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
            "normalizer_name": fields.TextField(attr="normalizer_name"),
        }
    ))
    keywords = fields.ListField(fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
            "normalizer_name": fields.TextField(attr="normalizer_name"),
        }
    ))
    geo = fields.GeoPointField()

    class Index:
        name = "merchants"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Merchant
        related_models = [Hashtag, Keyword]
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
        ]

    def get_queryset(self):
        return super(MerchantDocument, self).get_queryset().prefetch_related(
            "hashtags",
            "keywords",
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Hashtag):
            return related_instance.merchants.prefetch_related(
                "hashtags",
                "keywords",
            ).all()
        elif isinstance(related_instance, Keyword):
            return related_instance.merchants.prefetch_related(
                "hashtags",
                "keywords",
            ).all()


# @registry.register_document
# class ProductsDocument(Document):
#     hashtag = fields.ObjectField(
#         properties={
#             "id": fields.IntegerField(),
#             "name": fields.TextField(),
#         }
#     )
#     keyword = fields.ObjectField(
#         properties={
#             "id": fields.IntegerField(),
#             "name": fields.TextField(),
#         }
#     )
#     category = fields.ObjectField(
#         properties={
#             "id": fields.IntegerField(),
#             "name_vi": fields.TextField(),
#             "name_en": fields.TextField(),
#         }
#     )
#
#     class Index:
#         name = "products"
#         settings = {
#             "number_of_shards": 1,
#             "number_of_replicas": 0,
#         }
#
#     class Django:
#         model = Products
#         fields = [
#             "name",
#             "description",
#             "created_at",
#             "updated_at",
#         ]
#
#
# @registry.register_document
# class ServicesDocument(Document):
#     hashtag = fields.ObjectField(
#         properties={
#             "id": fields.IntegerField(),
#             "name": fields.TextField(),
#         }
#     )
#     keyword = fields.ObjectField(
#         properties={
#             "id": fields.IntegerField(),
#             "name": fields.TextField(),
#         }
#     )
#     category = fields.ObjectField(
#         properties={
#             "id": fields.IntegerField(),
#             "name_vi": fields.TextField(),
#             "name_en": fields.TextField(),
#         }
#     )
#
#     class Index:
#         name = "services"
#         settings = {
#             "number_of_shards": 1,
#             "number_of_replicas": 0,
#         }
#
#     class Django:
#         model = Services
#         fields = [
#             "name",
#             "description",
#             "created_at",
#             "updated_at",
#         ]

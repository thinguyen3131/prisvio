from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from prismvio.merchant.models import Merchant
from prismvio.menu_merchant.models import Category, Hashtag, Products, Services, Keyword

User = get_user_model()


@registry.register_document
class UserDocument(Document):
    class Index:
        name = 'users'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_number',
        ]

@registry.register_document
class CategoryDocument(Document):
    id = fields.IntegerField()

    class Index:
        name = 'categories'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Category
        fields = [
            'name_vi',
            'name_en'
            'notes',
        ]

@registry.register_document
class HashtagDocument(Document):
    id = fields.IntegerField()

    class Index:
        name = 'hastags'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Hashtag
        fields = [
            'name',
            'description',
        ]


@registry.register_document
class KeywordDocument(Document):
    id = fields.IntegerField()

    class Index:
        name = 'keywords'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Keyword
        fields = [
            'name',
            'description',
        ]

@registry.register_document
class MerchantDocument(Document):
    hashtag = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
    keyword = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
    class Index:
        name = 'merchants'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }
    class Django:
        model = Merchant
        fields = [
            'name',
            'description',
            'created_at',
            'updated_at',
        ]

@registry.register_document
class ProductsDocument(Document):
    hashtag = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
    keyword = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
    category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name_vi': fields.TextField(),
        'name_en': fields.TextField(),
    })
    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }
    class Django:
        model = Products
        fields = [
            'name',
            'description',
            'created_at',
            'updated_at',
        ]

@registry.register_document
class ServicesDocument(Document):
    hashtag = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
    keyword = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
    })
    category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name_vi': fields.TextField(),
        'name_en': fields.TextField(),
    })
    class Index:
        name = 'services'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }
    class Django:
        model = Services
        fields = [
            'name',
            'description',
            'created_at',
            'updated_at',
        ]
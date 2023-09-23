from django.conf import settings
from django.contrib.auth import get_user_model
from elasticsearch_dsl import Q, analyzer
from pydantic import BaseModel

from prismvio.core.dsl import fields
from prismvio.core.dsl.documents import Document
from prismvio.core.dsl.registries import registry
from prismvio.core.dsl.search import Search
from prismvio.menu_merchant.models import Category, Hashtag, Keyword
from prismvio.merchant.models import Merchant

User = get_user_model()

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


class MerchantSearchRequest(BaseModel):
    search_text: str
    latitude: float = settings.DEFAULT_LATITUDE
    longitude: float = settings.DEFAULT_LONGITUDE
    country_id: int | None = None
    province_id: int | None = None
    district_id: int | None = None
    ward_id: int | None = None
    user_id: int | None = None
    category_ids: list[int] | None = []
    distance: int | None = None
    offset: int = 0
    limit: int = 20


@registry.register_document
class MerchantDocument(Document):
    normalizer_name = fields.TextField(attr="normalizer_name")

    description = fields.TextField(analyzer=html_strip, fields={"raw": fields.KeywordField()})

    hashtags = fields.ListField(
        fields.ObjectField(
            properties={
                "id": fields.IntegerField(),
                "name": fields.TextField(),
                "normalizer_name": fields.TextField(attr="normalizer_name"),
            }
        )
    )
    keywords = fields.ListField(
        fields.ObjectField(
            properties={
                "id": fields.IntegerField(),
                "name": fields.TextField(),
                "normalizer_name": fields.TextField(attr="normalizer_name"),
            }
        )
    )
    categories = fields.ListField(
        fields.ObjectField(
            properties={
                "id": fields.IntegerField(),
                "name_vi": fields.TextField(),
                "name_en": fields.TextField(),
            }
        )
    )
    position = fields.GeoPointField(attr="position")
    country = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "full_name_vi": fields.KeywordField(),
            "full_name_en": fields.KeywordField(),
            "zip_code": fields.KeywordField(),
        }
    )
    province = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "code": fields.KeywordField(),
            "name_vi": fields.KeywordField(),
            "name_en": fields.KeywordField(),
            "zip_code": fields.KeywordField(),
        }
    )
    district = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "code": fields.KeywordField(),
            "name_vi": fields.KeywordField(),
            "name_en": fields.KeywordField(),
            "zip_code": fields.KeywordField(),
        }
    )
    ward = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "code": fields.KeywordField(),
            "name_vi": fields.KeywordField(),
            "name_en": fields.KeywordField(),
            "zip_code": fields.KeywordField(),
        }
    )

    country_id = fields.IntegerField(attr="country_id")
    province_id = fields.IntegerField(attr="province_id")
    district_id = fields.IntegerField(attr="district_id")
    ward_id = fields.IntegerField(attr="ward_id")
    user_id = fields.IntegerField(attr="user_id")

    hashtag_ids = fields.ListField(fields.IntegerField())
    category_ids = fields.ListField(fields.IntegerField())

    class Index:
        name = "merchants"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Merchant
        related_models = [Hashtag, Keyword, Category]
        fields = [
            "id",
            "name",
            "is_active",
            "uid",
            "address",
            "country_code",
            "total_bookings",
            "created_at",
            "updated_at",
        ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "hashtags",
                "keywords",
                "categories",
            )
            .select_related(
                "country",
                "province",
                "district",
                "ward",
            )
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Hashtag):
            return related_instance.merchants.get_with_related_data().all()
        elif isinstance(related_instance, Keyword):
            return related_instance.merchants.get_with_related_data().all()
        elif isinstance(related_instance, Category):
            return related_instance.merchants.get_with_related_data().all()

    def prepare(self, instance):
        data = super().prepare(instance)
        data["hashtag_ids"] = self.get_obj_ids(data, "hashtags")
        data["keyword_ids"] = self.get_obj_ids(data, "keywords")
        data["category_ids"] = self.get_obj_ids(data, "categories")
        return data


class MerchantSearch(Search):
    doc_types = [MerchantDocument]

    search_text_fields = [
        "name",
        "description",
        "normalizer_name",
        "hashtags.name",
        "hashtags.normalizer_name",
        "keywords.name",
        "keywords.normalizer_name",
    ]
    geo_point_field = "position"

    def __init__(self, **kwargs):
        super().__init__(model=Merchant)

    def custom_search(self, queryset, request: MerchantSearchRequest):
        must = [
            Q("term", is_active=True),
            self.get_query_string_query(request.search_text),
            *self.filter_by_fields(
                request,
                [
                    "country_id",
                    "province_id",
                    "district_id",
                    "ward_id",
                    "user_id",
                ],
            ),
        ]
        if request.category_ids:
            must.append(Q("terms", category_ids=request.category_ids))

        if request.distance:
            must.append(
                self.get_geo_distance_query(
                    request.latitude, request.longitude, field="position", distance=request.distance
                )
            )

        combined_queries = Q("bool", must=must)

        s = self.query(combined_queries)
        s = s.source(excludes=["*"])
        s = s.sort(
            self.get_distance_sort(request.latitude, request.longitude),
            {"total_bookings": {"order": "desc"}},
            self.get_datetime_sort("created_at"),
            {"_score": {"order": "desc"}},
        )
        s = s[request.offset : request.offset + request.limit]
        result = s.execute()
        return self.get_result(
            result,
            queryset,
        )

from django.db.models import Case, When
from django.db.models.fields import IntegerField
from elasticsearch_dsl import Q
from elasticsearch_dsl import Search as DSLSearch
from slugify import slugify


class Search(DSLSearch):
    search_text_fields = []
    geo_point_field = ""

    def __init__(self, **kwargs):
        self._model = kwargs.pop("model", None)
        super().__init__(**kwargs)

    def _clone(self):
        s = super()._clone()
        s._model = self._model
        return s

    def filter_queryset(self, queryset, keep_search_order=True):
        """
        Filter an existing django queryset using the elasticsearch result.
        It costs a query to the sql db.
        """
        s = self
        if s._model is not queryset.model:
            raise TypeError("Unexpected queryset model " "(should be: %s, got: %s)" % (s._model, queryset.model))

        # Do not query again if the es result is already cached
        if not hasattr(self, "_response"):
            # We only need the meta fields with the models ids
            s = self.source(excludes=["*"])
            s = s.execute()

        return self.get_result(s, queryset, keep_search_order)

    def get_result(self, search_results, queryset, keep_search_order=True):
        pks = [result.meta.id for result in search_results]
        queryset = queryset.filter(pk__in=pks)

        if keep_search_order:
            preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pks)], output_field=IntegerField())
            queryset = queryset.order_by(preserved_order)

        return queryset, search_results.hits.total.value

    def _get_queryset(self):
        """
        Return a django queryset that will be filtered by to_queryset method.
        """
        return self._model._default_manager.all()

    def to_queryset(self, keep_order=True):
        """
        Return a django queryset from the elasticsearch result.
        It costs a query to the sql db.
        """
        qs = self._get_queryset()
        return self.filter_queryset(qs, keep_order)

    def get_query_string_query(self, search_text):
        if not self.search_text_fields:
            raise ValueError("Define search_text_fields value")

        normalizer = slugify(search_text.strip(), word_boundary=True, separator=" ", lowercase=True)
        search_text_query = (
            f"(*{search_text}*) OR ({search_text}) OR " f"({normalizer.strip()}) OR (*{normalizer.strip()}*)"
        )

        return Q(
            "query_string",
            query=search_text_query,
            fields=self.search_text_fields,
            fuzziness="AUTO",
            fuzzy_transpositions=True,
            fuzzy_max_expansions=50,
            fuzzy_prefix_length=0,
            minimum_should_match=1,
            lenient=False,
            boost=1.0,
            allow_leading_wildcard=True,
            enable_position_increments=True,
            phrase_slop=3,
            max_determinized_states=1000,
            quote_field_suffix="",
            quote_analyzer="standard",
            analyze_wildcard=True,
            auto_generate_synonyms_phrase_query=True,
            rewrite="constant_score",
        )

    def get_distance_sort(self, latitude, longitude):
        if not self.geo_point_field:
            raise ValueError("Define geo_point_field value")

        return {
            "_geo_distance": {self.geo_point_field: {"lat": latitude, "lon": longitude}, "order": "asc", "unit": "km"}
        }

    def get_datetime_sort(self, datetime_field: str, order="desc"):
        return {
            datetime_field: {
                "order": order,
                "format": "strict_date_optional_time_nanos",
            }
        }

    def filter_by_fields(self, request, filter_fields: list[str]):
        result = []
        for field in filter_fields:
            value = getattr(request, field, None)
            if value:
                result.append(Q("term", **{field: value}))

        return result

    def get_geo_distance_query(self, latitude, longitude, field, distance=10):
        return Q("geo_distance", distance=f"{distance}km", **{field: {"lat": latitude, "lon": longitude}})

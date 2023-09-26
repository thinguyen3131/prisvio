import re

from django.core.exceptions import FieldError
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination


def build_field_mapping(model, exclude_fields=[]):
    fields = [x.name for x in model._meta.get_fields()]
    field_mapping = {field: field for field in fields if field not in exclude_fields}
    return field_mapping


def build_query_filters(params, field_mapping):
    list_or = []
    list_and = {}
    exclude = {}
    for key, value in params.items():
        if key in field_mapping.keys():
            filter_string = field_mapping[key]
            if isinstance(value, str):
                filter_string += "__icontains"
            elif isinstance(value, list):
                filter_string += "__in"
            if value.startswith("~"):
                list_or.append({filter_string: value[1:]})
            else:
                list_and.update({filter_string: value})
        if key != "sort_by":
            value = handle_search_phone_number_and_email(key, value)
        if key.endswith("isempty"):
            filter_string = key.replace("isempty", "exact")
            if value == "false":
                exclude.update({filter_string: ""})
            else:
                list_and.update({filter_string: ""})
    return list_or, list_and, exclude


def search(params=None, **kwargs):
    params = params or kwargs.get("query_params", {})
    pagination_class = kwargs.get("pagination_class", LimitOffsetPagination)
    model = kwargs.get("model", None)
    exclude_fields = kwargs.get("exclude_fields", [])
    custom_queryset = kwargs.get("queryset", None)

    field_mapping = build_field_mapping(model, exclude_fields)

    limit = params.get("limit", 10)
    offset = params.get("offset", 1)
    order_by = params.get("sort_by", "id")

    pagination_class.limit = limit
    pagination_class.offset = offset

    list_or, list_and, exclude = build_query_filters(params, field_mapping)
    queryset = custom_queryset if custom_queryset is not None else model.objects.all()

    q_object = Q()
    for query in list_or:
        q_object.add(Q(**query), Q.OR)

    try:
        queryset = queryset.filter(q_object).filter(**list_and).exclude(**exclude).order_by(order_by).distinct()
    except FieldError:
        queryset = queryset.none()

    pagination_class.queryset = queryset
    return queryset


def handle_whitespace(value, word):
    return re.sub(r"(\s+)", rf"{word}", value)


def handle_search_phone_number_and_email(key, value):
    if key not in ("phone_number", "email"):
        return value
    v = []
    for x in value.split(","):
        tmp_val = re.sub(r"(\s+)", r"+", x)
        if key == "phone_number":
            tmp_val = f"+{tmp_val}" if tmp_val.startswith("+") is False else tmp_val
        v.append(tmp_val)
    return v

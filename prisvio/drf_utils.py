import datetime
import functools
import re

from django.conf import settings
from django.core.exceptions import FieldError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404

from dateutil.parser import parse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework_extensions.mixins import NestedViewSetMixin

# from api.views import api_exception_handler


# class ImageFieldWithDefaultURLRepr(serializers.ImageField):
#     def __init__(self, default_url_repr=None, *args, **kwargs):
#         self.default_url_repr = default_url_repr
#         super().__init__(*args, **kwargs)

#     def to_representation(self, value):
#         if not value:
#             request = self.context.get('request', None)
#             if request is not None:
#                 return request.build_absolute_uri(self.default_url_repr)
#         return super().to_representation(value)


# def check_if_request(func):
#     @functools.wraps(func)
#     def wrapper(self, obj):
#         if not getattr(self.context.get('request'), 'user', None):
#             return None
#         return func(self, obj)
#     return wrapper


# class ExtendedNestedViewSetMixin(NestedViewSetMixin):
#     parent_object_class = None
#     parent_object_id_kwarg = None

#     def __init__(self, *args, **kwargs):
#         self._parent_object = None
#         super().__init__(*args, **kwargs)

#     def get_parent_object(self):
#         assert self.parent_object_class is not None, (
#             "'{0}' should include a 'parent_object_class' attribute".format(self.__class__.__name__))  # noqa: Q000
#         assert self.parent_object_id_kwarg is not None, (
#             "'{0}' should include a 'parent_object_id_kwarg' attribute".format(self.__class__.__name__))  # noqa: Q000

#         if self._parent_object is None:
#             self._parent_object = get_object_or_404(
#                 self.parent_object_class, pk=self.get_parents_query_dict()[self.parent_object_id_kwarg])
#         return self._parent_object

#     def get_parent_object_id(self):
#         assert self.parent_object_id_kwarg is not None, (
#             "'{0}' should include a 'parent_object_id_kwarg' attribute".format(self.__class__.__name__))  # noqa: Q000

#         if getattr(self, 'swagger_fake_view', False):
#             # queryset just for schema generation metadata
#             return 0

#         return self.get_parents_query_dict()[self.parent_object_id_kwarg]


# def exception_handler(exc, context):
#     """Handle Django ValidationError as an accepted exception
#     Must be set in settings:
#     >>> REST_FRAMEWORK = {
#     ...     # ...
#     ...     'EXCEPTION_HANDLER': 'mtp.apps.common.drf.exception_handler',
#     ...     # ...
#     ... }
#     For the parameters, see ``exception_handler``
#     """

#     if isinstance(exc, DjangoValidationError):
#         if hasattr(exc, 'message_dict'):
#             exc = DRFValidationError(detail={'error': exc.message_dict})
#         elif hasattr(exc, 'message'):
#             exc = DRFValidationError(detail={'error': exc.message})
#         elif hasattr(exc, 'messages'):
#             exc = DRFValidationError(detail={'error': exc.messages})

#     if settings.CUSTOM_ERROR_CODE:
#         return api_exception_handler(exc, context)

#     return drf_exception_handler(exc, context)


# def search(params=None, **kwargs):
#     if params is None:
#         params = {}
#     params = params or kwargs.get('query_params', {})
#     pagination_class = kwargs.get('pagination_class', LimitOffsetPagination)
#     mapping = kwargs.get('mapping', {})
#     model = kwargs.get('model', None)
#     exclude_fields = kwargs.get('exclude_fields', [])
#     custom_queryset = kwargs.get('queryset', None)

#     fields = [x.name for x in model._meta.get_fields()]
#     s_mapping = {}
#     for field in fields:
#         if field in exclude_fields:
#             continue
#         s_mapping.update(
#             {
#                 field: field,
#             },
#         )
#     s_mapping.update(**mapping)

#     try:
#         master_mapping = model._meta.app_config.models_module.master_mapping
#     except AttributeError:
#         master_mapping = {}
#     for key, value in master_mapping.items():
#         s_mapping.update({value: key})

#     limit = params.get('limit', 10)
#     offset = params.get('offset', 1)
#     order_by = params.get('sort_by', 'id')

#     pagination_class.limit = limit
#     pagination_class.offset = offset

#     list_or = []
#     list_and = {}
#     exclude = {}
#     is_multi = False
#     for key, value in params.items():
#         if value.startswith('~'):
#             value = value[1:]
#             start_with = '~'
#         else:
#             start_with = ''
#         if key != 'sort_by':
#             value = handle_search_phone_number_and_email(key, value)

#         if key in s_mapping.keys():  # Map key for searching
#             if value == 'true':
#                 value = True
#             elif value == 'false':
#                 value = False

#             filter_string = s_mapping[key]
#             if isinstance(value, str):
#                 if not key.endswith('id') and not key.endswith(
#                         'lte') and not key.endswith('gte') and not key.endswith('date') and not key.endswith('email'):
#                     filter_string += '__icontains'
#             elif isinstance(value, list):
#                 filter_string += '__in'

#             if start_with:
#                 list_or.append(
#                     {
#                         filter_string: value,
#                     },
#                 )
#             else:
#                 list_and.update(
#                     {
#                         filter_string: value,
#                     },
#                 )
#         if key.endswith('gte') or key.endswith('lte'):
#             match_date_time = re.search(r'\d+-\d+-\d+', str(value))
#             if match_date_time:
#                 if isinstance(parse(value), datetime.date):
#                     value = parse(value)
#             else:
#                 match_num = re.search('^[\d\.]+$', value)  # noqa: W605
#                 if match_num:
#                     value = float(value)

#             filter_string = s_mapping[key]
#             if start_with:
#                 list_or.append(
#                     {
#                         filter_string: value,
#                     },
#                 )
#             else:
#                 list_and.update(
#                     {
#                         filter_string: value,
#                     },
#                 )
#         # todo: workaround for search empty string
#         if key.endswith('isempty'):
#             filter_string = key.replace('isempty', 'exact')
#             if value == 'false':
#                 exclude.update(
#                     {
#                         filter_string: '',
#                     },
#                 )
#             else:
#                 if start_with:
#                     list_or.append(
#                         {
#                             filter_string: '',
#                         },
#                     )
#                 else:
#                     list_and.update(
#                         {
#                             filter_string: '',
#                         },
#                     )

#         if key == 'sort_by':
#             default_sort_key = 'id'
#             if ',' not in value:
#                 if value.startswith('-'):
#                     order_by = '{}{}'.format('-', s_mapping.get(value[1:]) or default_sort_key)
#                 else:
#                     order_by = s_mapping.get(value) or default_sort_key
#             else:
#                 order_by = [i.strip() for i in value.split(',')]
#                 is_multi = True

#     queryset = custom_queryset if custom_queryset is not None else model.objects
#     q_object = Q()
#     for x in list_or:
#         q_object.add(Q(**x), Q.OR)
#     try:
#         queryset = queryset.filter(q_object)
#         queryset = queryset.filter(**list_and)
#         queryset = queryset.exclude(**exclude)
#         queryset = queryset.order_by(order_by) if is_multi is False else queryset.order_by(*order_by)
#         queryset = queryset.distinct()
#     except FieldError:
#         pagination_class.queryset = queryset.none()
#         return queryset.none()

#     pagination_class.queryset = queryset

#     return queryset

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
                filter_string += '__icontains'
            elif isinstance(value, list):
                filter_string += '__in'
            if value.startswith('~'):
                list_or.append({filter_string: value[1:]})
            else:
                list_and.update({filter_string: value})
        if key.endswith('isempty'):
            filter_string = key.replace('isempty', 'exact')
            if value == 'false':
                exclude.update({filter_string: ''})
            else:
                list_and.update({filter_string: ''})
    return list_or, list_and, exclude

def search(params=None, **kwargs):
    params = params or kwargs.get('query_params', {})
    pagination_class = kwargs.get('pagination_class', LimitOffsetPagination)
    model = kwargs.get('model', None)
    exclude_fields = kwargs.get('exclude_fields', [])
    custom_queryset = kwargs.get('queryset', None)
   
    field_mapping = build_field_mapping(model, exclude_fields)
   
    limit = params.get('limit', 10)
    offset = params.get('offset', 1)
    order_by = params.get('sort_by', 'id')
   
    pagination_class.limit = limit
    pagination_class.offset = offset
   
    list_or, list_and, exclude = build_query_filters(params, field_mapping)
   
    queryset = custom_queryset if custom_queryset else model.objects.all()
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
    return re.sub(r'(\s+)', fr'{word}', value)


def handle_search_phone_number_and_email(key, value):
    if key not in ('phone_number', 'email'):
        return value
    v = []
    for x in value.split(','):
        tmp_val = re.sub(r'(\s+)', r'+', x)
        if key == 'phone_number':
            tmp_val = f'+{tmp_val}' if tmp_val.startswith('+') is False else tmp_val
        v.append(tmp_val)
    return v

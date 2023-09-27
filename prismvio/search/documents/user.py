from django.conf import settings
from elasticsearch_dsl import Q, analyzer
from pydantic import BaseModel

from prismvio.core.dsl import fields
from prismvio.core.dsl.documents import Document
from prismvio.core.dsl.registries import registry
from prismvio.core.dsl.search import Search
from django.contrib.auth import get_user_model
from prismvio.users.models.user import PrivacySetting
from elasticsearch_dsl.query import Nested

User = get_user_model()

class UserSearchRequest(BaseModel):
    search_text: str
    friend_ids: list[int] | None = None

@registry.register_document
class UsersDocument(Document):
    username = fields.KeywordField(attr='username')
    email = fields.KeywordField(attr='email')
    phone_number = fields.KeywordField(attr='phone_number')
    friend_ids = fields.ListField(fields.IntegerField())
    privacy_settings_id = fields.IntegerField(attr="privacy_settings_id")
    privacy_settings = fields.NestedField(properties={
        "id": fields.IntegerField(),
        'username_privacy': fields.KeywordField(),
        'email_privacy': fields.KeywordField(),
        'phone_number_privacy': fields.KeywordField(),
    })

    class Index:
        name = 'users'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = User
        fields = [
            'id',
        ]
        related_models = [PrivacySetting]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, PrivacySetting):
            return related_instance.user

    def get_queryset(self):
        return super().get_queryset().select_related('privacy_settings')


class UserSearch(Search):
    doc_types = [UsersDocument]

    search_text_fields = ['username', 'email', 'phone_number']

    def custom_search(self, queryset, request: UserSearchRequest):
        # must = [self.get_query_string_query(request.search_text)]
        user_name_condition = Q('term',  username = request.search_text)
        phone_number_condition = Q('term',  phone_number = request.search_text)
        email_condition = Q('term',  email = request.search_text)
        

        privacy_conditions_user_name = Nested(path="privacy_settings",query=Q('term', privacy_settings__username_privacy=PrivacySetting.EVERYONE))
        privacy_conditions_email = Nested(path="privacy_settings",query=Q('term', privacy_settings__email_privacy=PrivacySetting.EVERYONE))
        privacy_conditions_phone_number = Nested(path="privacy_settings",query=Q('term', privacy_settings__phone_number_privacy=PrivacySetting.EVERYONE))
        combined_queries = (user_name_condition & privacy_conditions_user_name) | (email_condition & privacy_conditions_email) | (phone_number_condition & privacy_conditions_phone_number)

        if request.friend_ids:
            friends_username_conditions = Nested(path='privacy_settings',
                                   query=Q('term', privacy_settings__username_privacy=PrivacySetting.FRIENDS))
            
            friends_email_conditions = Nested(path='privacy_settings',
                                   query=Q('term', privacy_settings__email_privacy=PrivacySetting.FRIENDS))
            friends_phone_number_conditions = Nested(path='privacy_settings',
                                   query=Q('term', privacy_settings__phone_number_privacy=PrivacySetting.FRIENDS))
            friend_id_conditions =  Q('terms', friend_ids=request.friend_ids)
            friends_conditions = (friend_id_conditions & friends_username_conditions & user_name_condition) | \
                                (friend_id_conditions & friends_email_conditions & email_condition) | \
                                (friend_id_conditions & friends_phone_number_conditions & phone_number_condition)

            combined_queries |= friends_conditions

        # must.append(privacy_conditions)
        # combined_queries = Q('bool', must=must)
        

        s = self.query(combined_queries)
        s = s.source(excludes=['*'])
        result = s.execute()
        return self.get_result(result, queryset)

# http://localhost:8000/search/?search_text=abc@gmail.com

# class UserSearch(Search):
#     doc_types = [UsersDocument]
    
#     def custom_search(self, queryset, request: UserSearchRequest):
#         must = []
#         should = []
        
#         # # Like search on username, email, and phone_number
#         search_text = request.search_text
#         if search_text:
#             should.append(Q("wildcard", username=f"*{search_text}*"))
#             should.append(Q("wildcard", email=f"*{search_text}*"))
#             should.append(Q("wildcard", phone_number=f"*{search_text}*"))
        
#         # PrivacySetting conditions apply
#         must.append(Q("term", privacy_settings__username_privacy=PrivacySetting.EVERYONE))
#         must.append(Q("term", privacy_settings__email_privacy=PrivacySetting.EVERYONE))
#         must.append(Q("term", privacy_settings__phone_number_privacy=PrivacySetting.EVERYONE))
        
#         # If the request is from a logged in user, add conditions for friends and only_me
#         user = request.user
#         if user.is_authenticated:
#             should.append(Q("bool", must=[
#                 Q("term", privacy_settings__username_privacy=PrivacySetting.FRIENDS),
#                 Q("term", user_id=user.id)  # user_id is the field containing the user's ID in the UserDocument
#             ]))
#             should.append(Q("bool", must=[
#                 Q("term", privacy_settings__email_privacy=PrivacySetting.FRIENDS),
#                 Q("term", user_id=user.id)
#             ]))
#             should.append(Q("bool", must=[
#                 Q("term", privacy_settings__phone_number_privacy=PrivacySetting.FRIENDS),
#                 Q("term", user_id=user.id)
#             ]))
        
#         # Combine all conditions
#         combined_queries = Q("bool", must=must, should=should, minimum_should_match=1)
        
#         s = self.query(combined_queries)
#         s = s[request.offset : request.offset + request.limit]
#         result = s.execute()
#         return self.get_result(result, queryset)
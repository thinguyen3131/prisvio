from django.contrib.auth import get_user_model
from pydantic import BaseModel

from prismvio.core.dsl.documents import Document
from prismvio.core.dsl.registries import registry

User = get_user_model()


class UserSearchRequest(BaseModel):
    search_text: str
    offset: int = 0
    limit: int = 20


@registry.register_document
class UsersDocument(Document):
    class Index:
        name = "users"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "parent_id",
        ]

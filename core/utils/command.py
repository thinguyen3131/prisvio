import json
import os

from django.conf import settings
from django.core.management import CommandError


def seed_data(file_path, model, key_fields=None, update=False, updated_fields=None):
    if key_fields is None:
        key_fields = ['slug']
    file_path = os.path.join(settings.BASE_DIR, file_path)
    if not os.path.isfile(file_path):
        raise CommandError(f'The file `{file_path}` does not exist.')

    json_data = open(file_path)
    data = json.load(json_data)
    json_data.close()
    for item in data:
        if 'fields' in item:
            try:
                query = dict()
                for key_field in key_fields:
                    if key_field in item['fields']:
                        query.update({
                            key_field: item['fields'][key_field],
                        })
                obj = model.objects.get(**query)
                if update and updated_fields and isinstance(updated_fields, list):
                    exclusion_keys = ['id', 'created_at', 'updated_at']
                    exclusion_keys += key_fields
                    for key_name in item['fields'].keys():
                        if key_name not in exclusion_keys and hasattr(obj, key_name):
                            if key_name in updated_fields:
                                setattr(obj, key_name, item['fields'][key_name])
                    obj.save()

            except model.DoesNotExist:
                model.objects.create(**item['fields'])

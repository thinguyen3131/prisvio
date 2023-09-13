from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from loguru import logger
import random
import string

class Command(BaseCommand):
    help = 'Seed users'

    def handle(self, *args, **options) -> None:
        User = get_user_model()
        users = [
            {
                'is_superuser': True,
                'email': 'admin@prismtech.vn',
                'password': '9!@YJtAhN7dt7VtVXhW4bv',
                'is_staff': True,
                'first_name': 'Admin',
                'last_name': 'PrismTech',
                'full_name': 'Admin PrismTech',
                'brand_name': 'PrismTech',
                'verified_email_at': timezone.now(),
                'profile_type': 3,
            }
        ]

        # for user_data in users:
        #     try:
        #         email = user_data.get('email')
        #         if email:
        #             User.objects.get(email=user_data['email'])
        #         else:
        #             logger.error('Please config your email')
        #     except User.DoesNotExist:
        #         User.objects.create_user(
        #             **user_data,
        #         )
        
        for i in range(100):
            random_email = ''.join(random.choices(string.ascii_lowercase, k=10)) + '@example.com'
            random_phone = ''.join(random.choices(string.digits, k=10))
            random_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=9))
            user_data = {
                'email': random_email if i % 2 == 0 else None,
                'phone_number': random_phone if i % 2 != 0 else None,
                'password': 'Vio!@2050',
                'first_name': random_name,
                'last_name': 'User',
                'full_name': f'{random_name} User',
                'profile_type': random.choice([1, 3]),
                'email_verified': True if i % 2 == 0 else False,
                'phone_verified': True if i % 2 != 0 else False,
            }
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(user_data)
            print(user_data['phone_number'])
            print("====================================================================================================================")

            try:
                if user_data.get('email'):
                    existing_user = User.objects.get(email=user_data['email'])
                    print("=============email============================",existing_user)
                elif user_data.get('phone_number'):
                    existing_user = User.objects.get(phone_number=user_data['phone_number'])
                    print("=============phone_number============================",existing_user)
            except ObjectDoesNotExist:
                print("=============phone_number============================")
                if user_data.get("phone_number") is not None:
                    phone_number["email"] = i
                
                created_user = User.objects.create_user(**user_data)
                parent_data = user_data.copy()
                parent_data['email'] = f"{created_user.email}_{created_user.id}@example.com" if user_data.get('email') else None
                parent_data['phone_number'] = str(int(created_user.phone_number) + 1) if created_user.phone_number else None
                parent_data['parent'] = created_user
                if user_data.get("phone_number") is not None:
                    phone_number["email"] = i+1
                User.objects.create_user(**parent_data)
                    


from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from merchant.models import Merchant


# Create your models here.
class Hashtag(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Promotion(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(default=None, null=True, blank=True)
    post_date = models.DateField(null=True, blank=False)
    post_time = models.TimeField(null=True, blank=True)
    close_post_date = models.DateField(null=True, blank=False)
    close_post_time = models.TimeField(null=True, blank=True)
    discount = models.FloatField()
    nuit = models.CharField(max_length=255, null=True, default=None)
    quantity = models.IntegerField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True,
                              blank=True,
                              on_delete=models.SET_NULL)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, related_name='promotion')
    products = models.ManyToManyField('Products', blank=True, related_name='promotions')
    services = models.ManyToManyField('Services', blank=True, related_name='promotions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=255, null=False)
    hashtags = models.ManyToManyField('Hashtag', related_name='products', blank=True)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=255, null=True, default=None)
    description = models.TextField(default=None)
    price = models.FloatField()
    images = models.JSONField(default=list, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, related_name='products')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True,
                              blank=True,
                              on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        return f'Product ID=[{self.id}]'


class Category(models.Model):
    name = models.CharField(max_length=50)
    parent_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='category')
    notes = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True,
                              blank=True,
                              on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0}, parent: {1}'.format(self.name, self.parent_id)


class Services(models.Model):
    name = models.CharField(max_length=255, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name='service')
    hashtags = models.ManyToManyField('Hashtag', related_name='service', blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    time = models.FloatField()
    time_date = models.CharField(max_length=255, null=True, default=None)
    fixed = models.BooleanField()
    price = models.FloatField()
    avalilable = models.IntegerField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              null=True,
                              blank=True,
                              on_delete=models.SET_NULL)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, related_name='service')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        return f'Service ID=[{self.id}]'
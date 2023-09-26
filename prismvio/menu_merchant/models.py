from django.conf import settings
from django.db import models
from slugify import slugify

from prismvio.merchant.models import Merchant
from prismvio.staff.models import Staff


class ServicesProductsManager(models.Manager):
    def get_with_related_data(self):
        return self.prefetch_related(
            "hashtags",
            "keyword",
        ).select_related(
            "merchant",
            "category",
        )


class Keyword(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def normalizer_name(self):
        if self.name:
            normalizer = slugify(self.name.strip(), word_boundary=True, separator=" ", lowercase=True)
            return normalizer
        return None


class Hashtag(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def normalizer_name(self):
        if self.name:
            normalizer = slugify(self.name.strip(), word_boundary=True, separator=" ", lowercase=True)
            return normalizer
        return None


class Category(models.Model):
    name_vi = models.CharField(max_length=50, default="SOME STRING")
    name_en = models.CharField(max_length=50, default="SOME STRING")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="category")
    notes = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    hashtag = models.OneToOneField(Hashtag, on_delete=models.CASCADE, null=True, blank=True, related_name="category")
    image = models.CharField(default=None, null=True, blank=True, max_length=1000)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name_en}, parent: {self.parent}"


class Promotion(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=False)
    end_date = models.DateTimeField(null=True, blank=False)
    discount = models.FloatField(null=True, blank=True, default=None)
    unit = models.CharField(max_length=255, null=True, blank=True, default=None)
    quantity = models.IntegerField(null=True, blank=True, default=None)
    type = models.CharField(max_length=255, null=True, blank=True, default="discount")
    buy_quantity = models.IntegerField(null=True, blank=True)
    get_quantity = models.IntegerField(null=True, blank=True)
    images = models.JSONField(default=list, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True, related_name="promotion")
    products = models.ManyToManyField("Product", blank=True, related_name="promotions")
    services = models.ManyToManyField("Service", blank=True, related_name="promotions")
    total_bookings = models.IntegerField(default=0, null=True, blank=True)
    all_day = models.BooleanField(default=False)
    is_happy_hour = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, null=False)
    hashtags = models.ManyToManyField(Hashtag, related_name="products", blank=True)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=255, null=True, default=None)
    description = models.TextField(default=None, null=True, blank=True)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, null=True, blank=True)
    images = models.JSONField(default=list, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="products")
    keywords = models.ManyToManyField(Keyword, blank=True, related_name="products")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    total_bookings = models.IntegerField(default=0, null=True, blank=True)
    hidden = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sold_quantity = models.IntegerField(default=0, help_text="Product sold quantity")
    objects = ServicesProductsManager()

    def __str__(self):
        if self.name:
            return self.name
        return f"Product ID=[{self.id}]"


class Service(models.Model):
    name = models.CharField(max_length=255, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="services")
    keywords = models.ManyToManyField(Keyword, blank=True, related_name="services")
    hashtags = models.ManyToManyField(Hashtag, related_name="services", blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    time = models.FloatField()
    time_date = models.CharField(max_length=255, null=True, default=None)
    require_staff = models.BooleanField(default=False)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, null=True, blank=True)
    available_slots = models.IntegerField()
    slots_unit = models.CharField(max_length=50, null=False, blank=True)
    use_total_available_slots = models.BooleanField(default=False)
    images = models.JSONField(default=list, null=True, blank=True)
    hidden = models.BooleanField(default=False)
    flexible_time = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    staff = models.ManyToManyField(Staff, blank=True, related_name="services")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    total_bookings = models.IntegerField(default=0, null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, related_name="services")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sold_quantity = models.IntegerField(default=0, null=True, blank=True, help_text="Service sold quantity")
    objects = ServicesProductsManager()

    def __str__(self):
        if self.name:
            return self.name
        return f"Service ID=[{self.id}]"

    def normalizer_name(self):
        if self.name:
            normalizer = slugify(self.name.strip(), word_boundary=True, separator=" ", lowercase=True)
            return normalizer
        return None


class Collection(models.Model):
    name = models.CharField(max_length=255, null=False)
    order = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, related_name="collection")
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        return f"Collection ID=[{self.id}]"

    def products(self):
        return self.collectionitem_set.filter(product__isnull=False)

    def services(self):
        return self.collectionitem_set.filter(service__isnull=False)


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    order = models.PositiveIntegerField()  # Thứ tự hiển thị

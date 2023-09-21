from django.db import models


# Create your models here.
class Country(models.Model):
    code = models.CharField(max_length=20, null=True, blank=True)
    full_name_vi = models.CharField(max_length=255)
    full_name_en = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Province(models.Model):
    code = models.CharField(max_length=20)
    name_vi = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def save(self, *args, **kwargs):
    #     if not self.code:
    #         self.code = str(self.id).zfill(2)  # Pad with zeros to make it 2 digits
    #     super(Province, self).save(*args, **kwargs)


class District(models.Model):
    code = models.CharField(max_length=20)
    name_vi = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Ward(models.Model):
    code = models.CharField(max_length=20)
    name_vi = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

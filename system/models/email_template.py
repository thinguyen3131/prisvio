from django.db import models
from django.utils.functional import cached_property

from tinymce.models import HTMLField

from system.enum import EmailTemplateLanguage


class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    code = models.SlugField(max_length=100, blank=False, null=False)
    language = models.CharField(max_length=100, null=False, choices=EmailTemplateLanguage.choices(),
                                default=EmailTemplateLanguage.ENG.value)
    use_mjml = models.BooleanField(default=True)
    mjml = models.TextField(default='', blank=True, null=True)
    html = HTMLField(default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ('code', 'language'),
        )

    def __str__(self):
        return self.name

    @cached_property
    def full_code(self):
        return f'{self.code}_{self.language}'

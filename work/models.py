from django.conf import settings
from django.db import models

class GeneratedWebsite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    css = models.TextField(blank=True)
    js = models.TextField(blank=True)
    prompt = models.TextField(blank=True)  # New field to store the user input (prompt)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "generated_website"  # Custom table name

    def __str__(self):  # Indentation fixed
        return f"{self.title} - {self.user.username}"


class Template(models.Model):
    CATEGORY_CHOICES = [
        ('business', 'Business'),
        ('portfolio', 'Portfolio'),
        ('ecommerce', 'E-commerce'),
        ('blog', 'Blog'),
        ('landing', 'Landing Page'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    theme = models.CharField(max_length=100, null=True, blank=True)
    code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='static/template_images/', null=True, blank=True)
    free = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

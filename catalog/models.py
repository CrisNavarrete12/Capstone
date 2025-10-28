from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='catalog_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user_id = models.CharField(max_length=100)
    food_1 = models.CharField(max_length=100)
    food_2 = models.CharField(max_length=100)
    food_3 = models.CharField(max_length=100)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)  # 🔥 NEW

    def __str__(self):
        return f"{self.user_id} - Veg: {self.is_vegetarian}, Vegan: {self.is_vegan}"

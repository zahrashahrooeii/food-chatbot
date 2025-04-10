from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)

    def __str__(self):
        return f"Conversation {self.id} ({'Vegetarian' if self.is_vegetarian else 'Vegan' if self.is_vegan else 'Non-Veg'})"

class FoodPreference(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='food_preferences', on_delete=models.CASCADE)
    food_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.food_name

class FoodCategory(models.Model):
    name = models.CharField(max_length=100)  # e.g., Italian, Asian, Fast Food
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Food Categories"

class Food(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, related_name='foods')
    health_score = models.FloatField(default=0.0)  # 0-10 scale
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    calories = models.IntegerField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    fats = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class Analytics(models.Model):
    date = models.DateField(auto_now_add=True)
    total_conversations = models.IntegerField(default=0)
    vegetarian_count = models.IntegerField(default=0)
    vegan_count = models.IntegerField(default=0)
    most_popular_food = models.CharField(max_length=200, null=True, blank=True)
    average_health_score = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = "Analytics"

    def __str__(self):
        return f"Analytics for {self.date}"

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    conversation_id = models.CharField(max_length=100)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Chat Histories"

    def __str__(self):
        return f"Chat {self.conversation_id} - {'Bot' if self.is_bot else 'User'}"

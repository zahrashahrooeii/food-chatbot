from django.contrib import admin
from .models import Conversation, FoodPreference, FoodCategory, Food, Analytics, ChatHistory

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'is_vegetarian', 'is_vegan')
    list_filter = ('is_vegetarian', 'is_vegan', 'created_at')
    search_fields = ('id',)

@admin.register(FoodPreference)
class FoodPreferenceAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'conversation', 'created_at')
    list_filter = ('conversation__is_vegetarian', 'conversation__is_vegan')
    search_fields = ('food_name',)

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'health_score', 'is_vegetarian', 'is_vegan', 'calories')
    list_filter = ('category', 'is_vegetarian', 'is_vegan')
    search_fields = ('name', 'category__name')

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_conversations', 'vegetarian_count', 'vegan_count', 'most_popular_food', 'average_health_score')
    list_filter = ('date',)

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_bot', 'created_at', 'conversation_id')
    list_filter = ('is_bot', 'created_at')
    search_fields = ('message', 'conversation_id')

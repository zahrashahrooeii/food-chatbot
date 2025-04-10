from django.core.management.base import BaseCommand
from food_api.models import FoodCategory, Food

class Command(BaseCommand):
    help = 'Initialize food categories and sample foods with health scores'

    def handle(self, *args, **kwargs):
        # Create food categories
        categories = {
            'Italian': 'Traditional Italian cuisine including pasta, pizza, and risotto',
            'Asian': 'Various Asian cuisines including Chinese, Japanese, and Thai',
            'Fast Food': 'Quick service restaurant foods',
            'Healthy': 'Nutritious and balanced meal options',
            'Desserts': 'Sweet treats and baked goods',
            'Mediterranean': 'Healthy Mediterranean diet options',
            'Mexican': 'Traditional Mexican dishes',
            'Indian': 'Rich and diverse Indian cuisine'
        }

        for name, description in categories.items():
            FoodCategory.objects.get_or_create(
                name=name,
                description=description
            )

        # Create sample foods with health scores
        foods_data = [
            # Italian
            {'name': 'Margherita Pizza', 'category': 'Italian', 'health_score': 6.5, 'is_vegetarian': True, 'calories': 266},
            {'name': 'Spaghetti Carbonara', 'category': 'Italian', 'health_score': 5.5, 'calories': 380},
            
            # Asian
            {'name': 'Sushi Roll', 'category': 'Asian', 'health_score': 8.0, 'calories': 250},
            {'name': 'Tofu Stir Fry', 'category': 'Asian', 'health_score': 9.0, 'is_vegetarian': True, 'is_vegan': True, 'calories': 220},
            
            # Fast Food
            {'name': 'Hamburger', 'category': 'Fast Food', 'health_score': 4.0, 'calories': 354},
            {'name': 'French Fries', 'category': 'Fast Food', 'health_score': 3.0, 'is_vegetarian': True, 'is_vegan': True, 'calories': 312},
            
            # Healthy
            {'name': 'Quinoa Bowl', 'category': 'Healthy', 'health_score': 9.5, 'is_vegetarian': True, 'is_vegan': True, 'calories': 280},
            {'name': 'Greek Salad', 'category': 'Healthy', 'health_score': 9.0, 'is_vegetarian': True, 'calories': 220},
            
            # Desserts
            {'name': 'Chocolate Cake', 'category': 'Desserts', 'health_score': 3.5, 'is_vegetarian': True, 'calories': 352},
            {'name': 'Fruit Sorbet', 'category': 'Desserts', 'health_score': 7.0, 'is_vegetarian': True, 'is_vegan': True, 'calories': 120},
            
            # Mediterranean
            {'name': 'Hummus', 'category': 'Mediterranean', 'health_score': 8.5, 'is_vegetarian': True, 'is_vegan': True, 'calories': 166},
            {'name': 'Falafel', 'category': 'Mediterranean', 'health_score': 7.5, 'is_vegetarian': True, 'is_vegan': True, 'calories': 333},
            
            # Mexican
            {'name': 'Guacamole', 'category': 'Mexican', 'health_score': 8.0, 'is_vegetarian': True, 'is_vegan': True, 'calories': 234},
            {'name': 'Bean Burrito', 'category': 'Mexican', 'health_score': 7.0, 'is_vegetarian': True, 'calories': 380},
            
            # Indian
            {'name': 'Vegetable Curry', 'category': 'Indian', 'health_score': 8.5, 'is_vegetarian': True, 'is_vegan': True, 'calories': 280},
            {'name': 'Chicken Tikka Masala', 'category': 'Indian', 'health_score': 6.5, 'calories': 325}
        ]

        for food_data in foods_data:
            category_name = food_data.pop('category')
            category = FoodCategory.objects.get(name=category_name)
            Food.objects.get_or_create(
                category=category,
                **food_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized food data')) 
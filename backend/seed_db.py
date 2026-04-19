# seed_db.py
import os
import sys

# מוודאים שתיקיית הפרויקט נמצאת בנתיב
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# מייבאים את האפליקציה, db ואת המודלים
from app import app, db
from models import User, Recipe, IngredientEntry

# סיסמה פשוטה לעת עתה
DUMMY_PASSWORD_HASH = "super_secure_admin_password_123"

def seed_data():
    with app.app_context():
        print("Starting data seeding...")

        # --- יצירת משתמש מנהל ---
        if User.query.filter_by(username='admin').first() is None:
            admin_user = User(
                username='admin', 
                password_hash=DUMMY_PASSWORD_HASH,
                role=9, # 9 = מנהל
                is_approved_uploader=True
            )
            admin_user.save()
            print("👤 User 'admin' created successfully.")
        else:
            admin_user = User.query.filter_by(username='admin').first()
            print("👤 User 'admin' already exists.")

        # --- יצירת מתכון לדוגמה ---
        if Recipe.query.filter_by(title='עוגת שוקולד קלה').first() is None:
            # 1. יצירת המתכון
            recipe_cake = Recipe(
                title='עוגת שוקולד קלה',
                description='עוגה שוקולדית בחושה, מהירה ומושלמת לימי חול.',
                prep_time=30, # 30 דקות
                category='חלבי',
                user_id=admin_user.id, # קישור למשתמש המנהל
                original_image_path='images/cake/original_path.jpg',
                variation_paths=['images/cake/small.jpg', 'images/cake/medium.jpg', 'images/cake/large.jpg']
            )
            recipe_cake.save()

            # 2. יצירת רכיבים (Ingredients)
            IngredientEntry(recipe_id=recipe_cake.id, name='קמח', quantity=2.0, unit='כוסות').save()
            IngredientEntry(recipe_id=recipe_cake.id, name='שוקולד מריר', quantity=100.0, unit='גרם').save()
            IngredientEntry(recipe_id=recipe_cake.id, name='ביצים', quantity=3.0, unit='יחידות').save()

            print("🍰 Recipe 'עוגת שוקולד קלה' created successfully.")
        else:
            print("🍰 Recipe 'עוגת שוקולד קלה' already exists.")

if __name__ == '__main__':
    seed_data()
    print("Seeding finished.")
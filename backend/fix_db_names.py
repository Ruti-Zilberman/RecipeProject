from app import app, db, Recipe
import os

def clean_name(name):
    if not name: return name
    # אותה לוגיקה של ניקוי שהשתמשנו בה בתיקייה
    return name.replace(" ", "_").replace("(", "").replace(")", "").replace("%20", "_")

def fix_database_records():
    with app.app_context():
        recipes = Recipe.query.all()
        print(f"מתחיל לתקן {len(recipes)} רשומות במסד הנתונים...")
        
        for recipe in recipes:
            # תיקון השם של התמונה הראשית
            old_main = recipe.imagePath
            new_main = clean_name(old_main)
            recipe.imagePath = new_main
            
            # תיקון השמות של הווריאציות
            if recipe.variation_paths:
                vars_list = recipe.variation_paths.split(',')
                new_vars = [clean_name(v) for v in vars_list]
                recipe.variation_paths = ",".join(new_vars)
            
            print(f"מתכון: {recipe.name} | עודכן ל: {new_main}")
        
        db.session.commit()
        print("✅ מסד הנתונים סונכרן עם השמות הנקיים!")

if __name__ == "__main__":
    fix_database_records()
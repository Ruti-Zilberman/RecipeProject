import os
import json
from app import app, db, User, Recipe, IngredientEntry
from PIL import Image, ImageFilter

# נתיב תיקיית ההעלאות
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')

def clean_filename(filename):
    """מנקה שם קובץ מרווחים וסימנים מיוחדים."""
    return filename.replace(" ", "_").replace("(", "").replace(")", "").replace("%20", "_")

def generate_variations(image_path):
    """יוצר וריאציות פיזיות לתמונה (שחור-לבן, סיבוב, טשטוש)."""
    try:
        if not os.path.exists(image_path):
            return ""
        
        img = Image.open(image_path)
        base_name, ext = os.path.splitext(os.path.basename(image_path))
        variations = []

        # 1. שחור-לבן
        bw_name = f"{base_name}_bw{ext}"
        img.convert("L").save(os.path.join(UPLOAD_FOLDER, bw_name))
        variations.append(bw_name)

        # 2. טשטוש
        blur_name = f"{base_name}_blur{ext}"
        img.filter(ImageFilter.GaussianBlur(3)).save(os.path.join(UPLOAD_FOLDER, blur_name))
        variations.append(blur_name)

        # 3. סיבוב
        rot_name = f"{base_name}_rot{ext}"
        img.rotate(5, expand=True).save(os.path.join(UPLOAD_FOLDER, rot_name))
        variations.append(rot_name)

        return ",".join(variations)
    except Exception as e:
        print(f"Error creating variations for {image_path}: {e}")
        return ""

def run_setup():
    with app.app_context():
        db.create_all() 
        print("--- טבלאות נוצרו בהצלחה ---")
        # הגנה: בקשת אישור מהמשתמש
        print("--- אזהרה: סנכרון נתונים חכם מתחיל ---")
        confirm = input("האם ברצונך לעדכן את בסיס הנתונים ולתקן שמות קבצים? (y/n): ")
        if confirm.lower() != 'y':
            print("הפעולה בוטלה.")
            return

        # שלב א': תיקון שמות קבצים פיזיים בתיקייה
        print("מתקן שמות קבצים בתיקייה...")
        for filename in os.listdir(UPLOAD_FOLDER):
            new_name = clean_filename(filename)
            if new_name != filename:
                os.rename(os.path.join(UPLOAD_FOLDER, filename), os.path.join(UPLOAD_FOLDER, new_name))

        # שלב ב': יצירת מנהל אם לא קיים
        admin = User.query.filter_by(role="Admin").first()
        if not admin:
            admin = User(Name="מנהל המערכת", Email="admin@test.com", password="123", role="Admin")
            db.session.add(admin)
            db.session.commit()

# שלב ג': רשימת מתכונים עשירה ומגוונת
        recipes_data = [
            # --- מאפים ומתוקים ---
            {"name": "עוגת שכבות וניל ופירות יער", "img": "Vanila-rasberry-cake-1.jpg", "type": "חלבי", "time": 60},
            {"name": "עוגת יום הולדת שוקולד חגיגית", "img": "עוגת_יום_הולדת.jpg", "type": "פרווה", "time": 90},
            {"name": "קינוח מוס שוקולד אישי", "img": "MG_6389.jpg", "type": "חלבי", "time": 40},
            {"name": "עוגה בחושה של סבתא", "img": "עוגה.jpg", "type": "פרווה", "time": 45},
            {"name": "גלידת וניל עם סירופ קרמל", "img": "vannila-caramel-icecream.jpg", "type": "חלבי", "time": 20},
            {"name": "עוגת קפה בחושה עשירה", "img": "coffeecake_inbal-720x480.jpg", "type": "פרווה", "time": 50},
            {"name": "בראוניז שוקולד וצ'אנקים", "img": "DrorEinavSugat4357-1-720x480.jpg", "type": "פרווה", "time": 35},

            # --- מנות עיקריות ובשרי ---
            {"name": "שיפודי פרגיות במרינדה", "img": "8348.jpg", "type": "בשרי", "time": 30},
            {"name": "בורקס בשר ביתי מבצק פריך", "img": "MG_8980.jpg", "type": "בשרי", "time": 55},
      
            {"name": "שלושת סוגי קובה ביתי", "img": "שלושת-הקובה.jpg", "type": "בשרי", "time": 150},
            {"name": "מאפה בשר וצנוברים", "img": "8321.jpg", "type": "בשרי", "time": 60},
            {"name": "כדורי בשר ברוטב עגבניות", "img": "IMG-20230206-WA0006.jpg", "type": "בשרי", "time": 45},

            # --- מנות קלות ופחמימות ---
            {"name": "פסטה איטלקית ברוטב עגבניות", "img": "1.webp", "type": "פרווה", "time": 25},
            {"name": "שקשוקה פיקנטית עם ביצים", "img": "2.JPG", "type": "פרווה", "time": 20},
            {"name": "מגש סושי מיקס יפני", "img": "8339.jpg", "type": "פרווה", "time": 80},
            {"name": "סלט ירוק רענן עם ויניגרט", "img": "8336.jpg", "type": "פרווה", "time": 15},
            {"name": "לחם קלוע כפרי", "img": "1_1.webp", "type": "פרווה", "time": 120},
            {"name": "ירקות קלויים בתנור", "img": "IMG-20230206-WA0004.jpg", "type": "פרווה", "time": 30}
        ]

        for data in recipes_data:
            clean_img = clean_filename(data["img"])
            if not Recipe.query.filter_by(name=data["name"]).first():
                print(f"יוצר מתכון: {data['name']}...")
                
                # יצירת וריאציות
                var_paths = generate_variations(os.path.join(UPLOAD_FOLDER, clean_img))
                
                new_r = Recipe(
                    name=data["name"],
                    imagePath=clean_img,
                    variation_paths=var_paths,
                    user_id=admin.id,
                    description=f"מתכון מעולה ל-{data['name']}",
                    prepTime=data["time"],
                    type=data["type"],    
                    instructions="1. הכנה. 2. בישול. 3. הגשה.",
                    rating=5.0
                )
                db.session.add(new_r)
                db.session.flush()
                
                # הוספת מרכיב לדוגמה
                db.session.add(IngredientEntry(Product="מרכיב בסיס", amount=1.0, unit="יחידה", recipe_id=new_r.id))

        db.session.commit()
        print("✅ הסנכרון הסתיים בהצלחה!")

if __name__ == "__main__":
    run_setup()
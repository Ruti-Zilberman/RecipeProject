# -*- coding: utf-8 -*-
# השורה הזו חשובה כדי שהערות בעברית לא יגרמו בעיות בקידוד

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from models import db, Recipe, User, IngredientEntry
from schemas import recipes_schema, recipe_schema, user_schema, users_schema
import os
import uuid 
import json 
from PIL import Image, ImageOps, ImageFilter
from werkzeug.security import generate_password_hash, check_password_hash
from schemas import ma  # מייבא את Marshmallow instance
from functools import wraps


# יוצרים את יישום Flask עם תיקיית static מוגדרת
app = Flask(__name__, static_folder='static')

# הגדרת CORS כדי לאפשר לאנגולר בחזיתית לקרוא לשרת מבלי לקבל חסימות
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- הגדרות בסיס נתונים ותיקיות ---
# קבלת הנתיב המוחלט של התיקיה הנוכחית (שבה app.py נמצא)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# הגדרה אחת סופית ואבסולוטית לתיקיית ההעלאות
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# הגדרת קישור לבסיס הנתונים SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
# כיבוי התראות שלא צריכים אותן
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# יצירת התיקיה אם היא לא קיימת
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# אתחול SQLAlchemy ו-Marshmallow עם יישום Flask
db.init_app(app)
ma.init_app(app)
# הפונקציה הזו היא הדוור שמוציא את הקובץ מהתיקייה הנסתרת בשרת ומגיש אותו לדפדפן.
# --- ה-Route שמחזיר תמונות שהו-Angular ביקש ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # משלחים את התמונה מתיקיית uploads
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- דקורטור (Decorator) שבודק אם משתמש הוא מנהל ---
def admin_required(f):
    """
    דקורטור זה משמר את הפונקציה המקורית (wraps) ובודק אם המשתמש הוא מנהל
    לפני שהיא מתבצעת. אם הוא לא, מחזירים שגיאה 403.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # שלוף את כתובת המנהל מה-Header של הבקשה
        # Flask לפעמים הופך Headers לאותיות קטנות ולכן משתמשים ב-get()
        admin_email = request.headers.get('Admin-Email')
        
        # אם לא הגיע Header עם אימייל מנהל, מחזירים שגיאה 401 (Unauthorized)
        if not admin_email:
            return jsonify({"message": "Missing Admin-Email header"}), 401
        
        # חיפוש המשתמש בבסיס הנתונים על פי האימייל
        user = User.query.filter_by(Email=admin_email).first()
        
        # אם לא מצאנו את המשתמש או שהוא לא בעל תפקיד Admin, מחזירים שגיאה 403 (Forbidden)
        if not user or user.role != 'Admin':
            return jsonify({"message": "Admin access required"}), 403
        
        # אם הכל בסדר, מריצים את הפונקציה המקורית
        return f(*args, **kwargs)
    return decorated_function

# --- פונקציה שמחזירה רק את המתכונים של משתמש מסוים ---
@app.route('/api/my-recipes/<int:user_id>', methods=['GET'])
def get_user_recipes(user_id):
    """
    שליפת כל המתכונים ששייכים ל-ID של משתמש מסוים.
    זה משמש לעמוד האישי כדי להציג רק את המתכונים שהמשתמש יצר.
    """
    # שליפה מהבסיס נתונים של כל מתכונים בעלי user_id תואם
    user_recipes = Recipe.query.filter_by(user_id=user_id).all()
    # המרה לפורמט JSON באמצעות Marshmallow schema
    return jsonify(recipes_schema.dump(user_recipes)), 200


# --- Route שמחזיר את כל המשתמשים (רק ללמנהל) ---
@app.route('/users', methods=['GET'])
@admin_required  # דקורטור בודק שהמשתמש הוא מנהל
def get_users():
    """
    קבלת רשימה של כל המשתמשים במערכת.
    רק מנהל יכול לגשת לשם.
    """
    try:
        # שליפה של כל המשתמשים מהבסיס נתונים
        all_users = User.query.all()
        # ייבוא בתוך הפונקציה (Lazy Import) נועד למנוע שגיאת "ייבוא מעגלי" (Circular Import) בין הקבצים השונים בפרויקט.
        # ייבוא ה-schema של Marshmallow עבור המרת משתמשים ל-JSON
        from schemas import users_schema
        data = users_schema.dump(all_users)
        return jsonify(data), 200
    except Exception as e:
        # הדפסת הבעיה לטרמינל כדי שנוכל לדבג
        print(f"❌ שגיאה בשליפת משתמשים: {str(e)}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# --- Route שמחזיר את כל המתכונים ---
@app.route('/recipes', methods=['GET'])
def get_recipes():
    """
    קבלת רשימה של כל המתכונים במערכת.
    משמש לעמוד הבית ולהצגה הכללית של כל המתכונים.
    """
    try:
        # שליפה של כל המתכונים
        all_recipes = Recipe.query.all()
        output = []
        # ה-URL הבסיסי של השרת
        base_url = "http://localhost:5000/"

        # לולאה על כל מתכון
        for recipe in all_recipes:
            # 1. חילוץ רשימת המרכיבים
            ingredients_list = []
            if hasattr(recipe, 'ingredients'):
                for ing in recipe.ingredients:
                    ingredients_list.append({
                        "product": getattr(ing, 'Product', 'לא ידוע')
                    })

            # 2. פונקציית עזר להמרת נתיבים לURLs מלאות
            def format_url(path):
                if not path: 
                    return ''
                # אם זה כבר URL מלא, אל תשנה אותו
                if path.startswith('http'): 
                    return path
                # הסרת leading slash כדי למנוע סלאש כפול
                clean_path = path.lstrip('/')
                return base_url + clean_path

            # 3. בניית URL מלא לתמונה הראשית
            raw_image_path = getattr(recipe, 'imagePath', '')
            full_image_path = format_url(raw_image_path)

            # 4. בניית רשימת וריאציות התמונות (גלריה)
            variation_str = getattr(recipe, 'variation_paths', '')
            variation_list = []
            if variation_str:
                # פיצול הוריאציות לפי פסיק וניקוי רווחים
                raw_variants = [p.strip() for p in variation_str.split(',') if p.strip()]
                variation_list = [format_url(v) for v in raw_variants]

            # 5. בניית האובייקט הסופי להחזרה לאנגולר
            output.append({
                "id": recipe.id,
                "name": getattr(recipe, 'name', 'ללא שם'),
                "description": getattr(recipe, 'description', ''),
                "prepTime": getattr(recipe, 'prepTime', 0),
                "type": getattr(recipe, 'type', 'פרווה'),
                "rating": getattr(recipe, 'rating', 5),
                "imagePath": full_image_path,
                "variation_paths": variation_list,
                "ingredients": ingredients_list
            })

        return jsonify(output), 200

    except Exception as e:
        print(f"Error fetching recipes: {e}")
        return jsonify({"message": str(e)}), 500

# ---פרטי מתכון -Route שמחזיר מתכון אחד לפי ID ---
@app.route('/recipes/<int:id>', methods=['GET'])
def get_recipe_by_id(id):
    """
    קבלת מתכון ספציפי לפי ה-ID שלו.
    משמש לעמוד הפרטים של מתכון בודד.
    """
    try:
        # חיפוש המתכון לפי ID
        recipe = Recipe.query.get(id)
        if recipe is None:
            return jsonify({"message": "מתכון לא נמצא"}), 404
        
# אתחול ערכי None למספרים (0 או 5.0) כדי למנוע שגיאות חישוב וקריסות תצוגה בצד הלקוח (Angular).
# אם אין נתון על כמות המדרגים, נגדיר אותה כ-0 כדי לאפשר חישובים מתמטיים
        if recipe.rating_count is None: 
            recipe.rating_count = 0

        # אם סכום הדירוגים ריק, נגדיר אותו כ-0.0 כדי למנוע שגיאות בחישוב הממוצע
        if recipe.total_rating_sum is None: 
            recipe.total_rating_sum = 0.0

        # אם למתכון אין דירוג עדיין, נציג ציון ברירת מחדל של 5 כוכבים
        if recipe.rating is None: 
            recipe.rating = 5.0        
        # המרה לJSON בעזרת Marshmallow schema
        return recipe_schema.jsonify(recipe)
    except Exception as e:
        print(f"🔥 שגיאת שרת במתכון {id}: {e}")
        return jsonify({"error": str(e)}), 500

# --- Route שמחזיר מתכון בודד עם פרטים מלאים ---
@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_single_recipe(recipe_id):
    """
    קבלת מתכון ספציפי עם כל הפרטים כולל מרכיבים.
    משמש לעמוד עריכה או תצוגה מפורטת.
    """
    try:
        # חיפוש המתכון, אם לא קיים Flask יחזיר 404 אוטומטית
        recipe = Recipe.query.get_or_404(recipe_id)
        
        # פורמטוב של המרכיבים להחזרה
        formatted_ingredients = []
        for ing in recipe.ingredients:
            formatted_ingredients.append({
                "name": ing.Product,  # שם המרכיב (Product בבסיס הנתונים)
                "amount": ing.amount,  # כמות
                "unit": ing.unit  # היחידה (גרם, כוס וכו')
            })

        # בניית האובייקט המלא
        return jsonify({
            "id": recipe.id,
            "title": getattr(recipe, 'title', getattr(recipe, 'name', '')),
            "description": recipe.description,
            "instructions": recipe.instructions,
            "prepTime": recipe.prepTime,
            "type": recipe.type,
            "ingredients": formatted_ingredients
        }), 200
    except Exception as e:
        print(f"!!! Flask Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# --- Route להרשמה של משתמש חדש ---
@app.route('/register', methods=['POST'])
def register():
    """
    יצירת משתמש חדש במערכת.
    מקבל: שם, אימייל, סיסמה
    בודק שהאימייל לא קיים, מצפין את הסיסמה, ושומר למסד הנתונים.
    """
    try:
        # קבלת הנתונים מה-JSON של הבקשה
        # חילוץ הנתונים שנשלחו מה-Client (אנגולר) והמרתם ממבנה JSON למילון פייתון נגיש.
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        # בדיקה שכל השדות הכרחיים הגיעו
        if not email or not password or not name:
            return jsonify({"message": "חסרים פרטים"}), 400

        # בדיקה אם המשתמש עם אותו אימייל כבר קיים
        user_exists = User.query.filter_by(Email=email).first()
        if user_exists:
            return jsonify({"message": "האימייל כבר קיים במערכת"}), 400

        # צפנת הסיסמה באמצעות pbkdf2:sha256
        # זה משמר כך שאנחנו לעולם לא שומרים את הסיסמה המקורית בבסיס הנתונים
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # יצירת משתמש חדש עם הסיסמה המצפנת
        new_user = User(Name=name, Email=email, password=hashed_password)
        
        # הוספה למסד הנתונים
        db.session.add(new_user)
        db.session.commit()
        
        # החזרה של פרטי המשתמש החדש
        return jsonify({
            "message": "הרישום בוצע בהצלחה!",
            "id": new_user.id,
            "userName": new_user.Name,
            "email": new_user.Email,
            "role": new_user.role or 'User'
        }), 201

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"message": "שגיאה בשרת"}), 500

# --- Route להתחברות (Login) ---
@app.route('/login', methods=['POST'])
def login():
    """
    התחברות של משתמש קיים.
    בודק את האימייל והסיסמה, ומחזיר את פרטי המשתמש אם הכל בסדר.
    """
    try:
        # קבלת הנתונים מה-JSON
        data = request.get_json()
        email_input = data.get('email')
        password_input = data.get('password')
        print(f"DEBUG: Trying to login with email: {email_input}")
        
        # חיפוש המשתמש לפי אימייל
        user = User.query.filter_by(Email=email_input).first()
        print(f"DEBUG: User found: {user}")
        
        # בדיקה אם המשתמש קיים וגם אם הסיסמה נכונה
        # check_password_hash השוואה בין הסיסמה שהוקלדה ל-Hash ששמור
        if user and check_password_hash(user.password, password_input):
            print(f"DEBUG: Password match!")
            # החזרה של פרטי ההתחברות המשתמש
            return jsonify({
             "message": "Login successful",
             "id": user.id,
             "role": user.role,
             "email": user.Email,
             "userName": user.Name
            }), 200
        
        # אם לא מצאנו משתמש או סיסמה לא נכונה
        return jsonify({"message": "אימייל או סיסמה שגויים"}), 401

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Internal Server Error"}), 500

# פונקציית עזר פנימית לניהול קבצים בשרת; היא אינה חשופה כ-Route כדי למנוע גישה חיצונית ישירה למערכת הקבצים
def delete_recipe_files(recipe):
    """מוחקת פיזית את כל התמונות של המתכון מהתיקייה בשרת"""
    # 1. מציאת הנתיב לתיקייה שבה שמורות התמונות
    base_dir = app.config['UPLOAD_FOLDER']
    files_to_delete = []
    
    # 2. הוספת התמונה הראשית לרשימת המחיקה
    if recipe.imagePath:
        files_to_delete.append(recipe.imagePath)
    
    # 3. הוספת כל התמונות המשניות (הוריאציות) לרשימת המחיקה
    if recipe.variation_paths:
        # split(',') הופך את המחרוזת מהמסד לרשימה של שמות קבצים
        files_to_delete.extend(recipe.variation_paths.split(','))
    
    # 4. המחיקה הפיזית מהכונן הקשיח
    for filename in files_to_delete:
        # בניית הנתיב המלא לקובץ
        file_path = os.path.join(base_dir, filename)
        # בדיקה שהקובץ באמת קיים לפני שמנסים למחוק (כדי למנוע קריסה)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ הקובץ {filename} נמחק בהצלחה מהשרת")

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    try:
        # קודם מנקים את השרת מהקבצים
        delete_recipe_files(recipe)
        
        # אחר כך מוחקים מהמסד
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "המתכון והתמונות נמחקו מהשרת ומהמסד"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/recipes/create', methods=['POST'])
def create_recipe():
    """
    יצירת מתכון חדש.
    משתמשת בפונקציות העזר לעיבוד תמונה (WebP) ושמירת מרכיבים.
    """
    try:
        # 1. שליפת נתונים בסיסיים
        user_email = request.form.get('email')
        user = User.query.filter_by(Email=user_email).first()
        
        if not user:
            return jsonify({"message": "User not found"}), 404

        # 2. עיבוד התמונה ל-WebP ווריאציות
        image_file = request.files.get('image')
        img_name, img_variants = (None, "")
        if image_file:
            img_name, img_variants = process_recipe_image(image_file)

        # 3. יצירת אובייקט המתכון
        new_recipe = Recipe(
            name=request.form.get('title'),
            description=request.form.get('description'),
            instructions=request.form.get('instructions'),
            prepTime=int(request.form.get('prepTime', 0)),
            type=request.form.get('type'),
            imagePath=img_name,
            variation_paths=img_variants,
            user_id=user.id
        )
        
        db.session.add(new_recipe)
        db.session.flush()  # מאפשר לנו לקבל את ה-ID של המתכון החדש מיד

        # 4. שמירת המרכיבים (באמצעות פונקציית העזר שסידרנו)
        ingredients_json = request.form.get('ingredients')
        if ingredients_json:
            save_recipe_ingredients(new_recipe.id, ingredients_json)

        db.session.commit()


        return jsonify({
            "message": "Recipe added successfully!", 
            "id": new_recipe.id
        }), 201

    except Exception as e:
        # במידה וקרתה תקלה (למשל: בעיה בתמונה או בחיבור למסד), מבצעים "חזרה אחורה".
        # זה מונע ממסד הנתונים להישאר "נעול" או לשמור חצי נתונים שיגרמו לשגיאות בבקשות הבאות.
        db.session.rollback()
        
        # מדפיס את השגיאה המדויקת לטרמינל שלך (בלבד) כדי שתוכלי לדבג ולראות מה קרה.
        print(f"Error in create_recipe: {str(e)}")
        
        # מחזיר תשובה מסודרת לצד הלקוח (Frontend) כדי שהאתר לא "ייתקע" בהמתנה.
        # הקוד 500 אומר: "קרתה שגיאת שרת פנימית".
        return jsonify({
            "message": "אופס! משהו השתבש בניסיון לשמור את המתכון.", 
            "error": str(e)
        }), 500    

@app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    """
    עדכון מתכון קיים.
    כולל החלפת תמונות (WebP), מחיקת ישנות ועדכון מרכיבים.
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    
    try:
        # 1. עדכון שדות טקסט בסיסיים
        recipe.name = request.form.get('title', recipe.name)
        recipe.description = request.form.get('description', recipe.description)
        recipe.instructions = request.form.get('instructions', recipe.instructions)
        recipe.prepTime = int(request.form.get('prepTime', recipe.prepTime))
        recipe.type = request.form.get('type', recipe.type)

        # 2. עדכון מרכיבים (משתמש בפונקציית העזר החדשה)
        ingredients_json = request.form.get('ingredients')
        if ingredients_json:
            save_recipe_ingredients(recipe.id, ingredients_json)

        # 3. עדכון תמונה - רק אם הועלה קובץ חדש
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # מחיקת הקבצים הישנים מהשרת (כדי שלא יישארו קבצי רפאים)
                delete_recipe_files(recipe)
                
                # עיבוד התמונה החדשה ל-WebP ועדכון הנתיבים במסד
                img_name, img_variants = process_recipe_image(file)
                recipe.imagePath = img_name
                recipe.variation_paths = img_variants

        # 4. שמירה סופית
        db.session.commit()
        
        return jsonify({
            "message": "המתכון עודכן בהצלחה!",
            "imagePath": recipe.imagePath
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error in update_recipe: {str(e)}")
        return jsonify({"message": "חלה שגיאה בעדכון המתכון", "error": str(e)}), 500   
#  
def save_recipe_ingredients(recipe_id, ingredients_json):
    """
    שמירת מרכיבי המתכון במסד הנתונים.
    הפונקציה תומכת גם ביצירה חדשה וגם בעדכון של מתכון קיים.
    """    
    if not ingredients_json: return
    # מחיקת מרכיבים קיימים אם יש (למקרה של עדכון)
    IngredientEntry.query.filter_by(recipe_id=recipe_id).delete()
    ingredients_list = json.loads(ingredients_json)
# מעבר על כל מרכיב ברשימה והוספתו לטבלת המרכיבים
    for ing in ingredients_list:
        db.session.add(IngredientEntry(
            # שימוש ב-.get() מונע קריסה אם אחד השדות חסר בטעות
            Product=ing.get('name'), 
            amount=ing.get('amount'),
            unit=ing.get('unit'),
            recipe_id=recipe_id # קישור המרכיב למתכון הספציפי
        ))
# --- פונקציות עזר לעיבוד תמונות ושמירת מרכיבים --- 
def process_recipe_image(image_file):
    """
    מעבדת תמונה חדשה: הופכת ל-WebP ומייצרת 3 ווריאציות.
    מחזירה: (שם_קובץ_ראשי, מחרוזת_ווריאציות)
    """
    # יצירת מזהה ייחודי וסיומת webp
    unique_id = str(uuid.uuid4())
    main_filename = f"{unique_id}.webp"
    base_dir = app.config['UPLOAD_FOLDER']
    full_path = os.path.join(base_dir, main_filename)

    with Image.open(image_file) as img:
        # המרה ל-RGB (חובה ל-WebP אם המקור הוא PNG עם שקיפות)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # שמירת התמונה הראשית
        img.save(full_path, "WEBP", quality=80)

        variants = []
        
        # 1. שחור-לבן
        bw_name = f"{unique_id}_bw.webp"
        ImageOps.grayscale(img).save(os.path.join(base_dir, bw_name), "WEBP")
        variants.append(bw_name)

        # 2. סיבוב
        rot_name = f"{unique_id}_rot.webp"
        img.rotate(90, expand=True).save(os.path.join(base_dir, rot_name), "WEBP")
        variants.append(rot_name)

        # 3. טשטוש
        blur_name = f"{unique_id}_blur.webp"
        img.filter(ImageFilter.GaussianBlur(5)).save(os.path.join(base_dir, blur_name), "WEBP")
        variants.append(blur_name)

    return main_filename, ",".join(variants)
# 1. קבלת כל המשתמשים במערכת
@app.route('/admin/users', methods=['GET'])
@admin_required  # בדיקה שהמשתמש הוא Admin
def get_all_users():
    """
    שליפה של כל המשתמשים עם פרטיהם.
    משמש לדשבורד המנהל.
    """
    try:
        # שליפה של כל המשתמשים
        users = User.query.all()
        users_list = []
        # בניית רשימה של אובייקטים עם פרטי כל משתמש
        for u in users:
            users_list.append({
                'id': u.id,
                'name': u.Name,
                'email': u.Email,
                'role': u.role,
                'is_approved': getattr(u, 'is_approved_uploader', False),
                'request_pending': getattr(u, 'request_pending', False)
            })
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# 2. אישור משתמש להיות Content Creator
@app.route('/approve_user/<int:user_id>', methods=['POST'])
@admin_required
def approve_user(user_id):
    """
    שינוי תפקיד משתמש מ-User ל-ContentCreator
    וסימון שאושר להעלות מתכונים.
    """
    try:
        # חיפוש המשתמש לפי ID
        user = User.query.get(user_id)
        if user:
            # עדכון התפקיד והדגלים
            user.role = 'ContentCreator'
            user.is_approved_uploader = True
            user.request_pending = False
            db.session.commit()
            return jsonify({"message": "המשתמש אושר בהצלחה!"}), 200
        
        return jsonify({"message": "משתמש לא נמצא"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

# 3. מחיקת משתמש מהמערכת
@app.route('/delete_user/<int:user_id>', methods=['DELETE']) # שיניתי את הנתיב שיתאים למה שהדפדפן מחפש
@admin_required
def delete_user(user_id):
    """
    מחיקת משתמש, כל המתכונים שלו וכל קבצי התמונות שלהם מהשרת.
    """
    try:
        # 1. חיפוש המשתמש
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "משתמש לא נמצא"}), 404
        
        # 2. ניקוי קבצים: עוברים על כל מתכון של המשתמש ומוחקים את התמונות שלו מהתיקייה
        if hasattr(user, 'recipes'):
            for recipe in user.recipes:
                # מחיקת הקבצים הפיזיים מהתיקייה
                delete_recipe_files(recipe)
                # מחיקת המתכון עצמו ממסד הנתונים (כדי לא לחסום את מחיקת המשתמש)
                db.session.delete(recipe)       
        # 3. מחיקה מהבסיס נתונים
        # הערה: אם מוגדר Cascade ב-Model, זה ימחק אוטומטית גם את השורות של המתכונים
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "המשתמש וכל קבצי התמונות שלו נמחקו בהצלחה"}), 200
        
    except Exception as e:
        db.session.rollback()
        # הדפסת השגיאה לטרמינל כדי שתוכלי לראות מה קרה אם זה נכשל
        print(f"Error deleting user: {str(e)}")
        return jsonify({"message": f"שגיאה במחיקה: {str(e)}"}), 500

        
@app.route('/recipes/search', methods=['POST'])
def search_recipes_by_ingredients():
    try:
        data = request.get_json()
        user_input = data.get('ingredients', '')
        
        # ניקוי מילות החיפוש
        user_words = user_input.lower().replace(',', ' ').split()
        user_ingredients_set = set([word.strip() for word in user_words if word.strip()])
        
        all_recipes = Recipe.query.all()
        results = []

        # מקרה חיפוש ריק - מחזירים הכל עם כל השדות
        if not user_ingredients_set:
            return jsonify([{
                "id": r.id, "name": r.name, "description": r.description,
                "prepTime": r.prepTime, "type": r.type, "rating": r.rating or 0,
                "imagePath": r.imagePath, "matchScore": 100
            } for r in all_recipes]), 200
        for recipe in all_recipes:
            # 1. רשימת המצרכים של המתכון הנוכחי (באותיות קטנות)
            recipe_ingredients = [ing.Product.lower() for ing in recipe.ingredients]
            total_ingredients_in_recipe = len(recipe_ingredients)

            if total_ingredients_in_recipe == 0:
                continue

            # 2. ספירה כמה מצרכים מהמתכון קיימים אצל המשתמש
            matches = 0
            for ing_name in recipe_ingredients:
                # בדיקה האם המצרך (או חלק ממנו) נמצא בסט המילים של המשתמש
                if any(user_word in ing_name for user_word in user_ingredients_set):
                    matches += 1
            
            # 3. חישוב הציון: כמה יש לי מתוך כמה שצריך
            if matches > 0:
                score = (matches / total_ingredients_in_recipe) * 100
                results.append({
                    "id": recipe.id,
                    "name": recipe.name,
                    "description": recipe.description,
                    "prepTime": recipe.prepTime,
                    "type": recipe.type,
                    "rating": recipe.rating or 0,
                    "imagePath": recipe.imagePath,
                    "matchScore": round(score, 1)
                })


        results.sort(key=lambda x: x['matchScore'], reverse=True)
        return jsonify(results), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": str(e)}), 500

# --- Route לדירוג מתכון ---
@app.route('/recipes/<int:recipe_id>/rate', methods=['POST'])
def rate_recipe(recipe_id):
    """
    קבלת דירוג חדש מהמשתמש וחישוב הממוצע החדש.
    """
    # קבלת הדירוג החדש (1-5 כוכבים)
    data = request.json
    new_stars = data.get('rating')
    
    # חיפוש המתכון
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # עדכון סכומי הדירוגים ומספר הדירוגים
    recipe.rating_count += 1
    recipe.total_rating_sum += new_stars
    # חישוב הממוצע החדש ועיגול לספרה אחת
    recipe.rating = round(recipe.total_rating_sum / recipe.rating_count, 1)
    
    # שמירה בבסיס הנתונים
    db.session.commit()
    
    # החזרה של הדירוג החדש
    return jsonify({
        "message": "Rating updated",
        "new_average": recipe.rating,
        "count": recipe.rating_count
    }), 200


# --- Route לבקשה על תפקיד Content Creator ---
@app.route('/api/request-content-role/<int:user_id>', methods=['POST'])
def request_content_role(user_id):
    """
    סימון שהמשתמש ביקש לקבל הרשאה להעלות מתכונים.
    המנהל יצטרך לאשר את הבקשה.
    """
    # חיפוש המשתמש
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "משתמש לא נמצא"}), 404
    
    # סימון שיש בקשה ממתינה
    user.request_pending = True
    db.session.commit()
    return jsonify({"message": "בקשה נשלחה למנהל"}), 200

# --- Route לקבלת פרטי משתמש ---
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    קבלת פרטי משתמש ספציפי לפי ID.
    """
    try:
        # חיפוש המשתמש
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        # החזרה של פרטי המשתמש
        return jsonify({
            "id": user.id,
            "userName": user.Name,      # ✅ CORRECT - עם N גדול
            "email": user.Email,
            "role": user.role,
            "is_content_user": user.is_approved_uploader,  # או is_content_user אם יש לו
  # האם בעל הרשאה להעלות מתכונים
            "request_pending": user.request_pending   # האם ממתין לאישור
        }), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# --- ריצה של היישום ---
if __name__ == '__main__':
    with app.app_context():
        try:
            print("--- מתחיל תהליך Seed ---")
            # יצירת כל הטבלאות אם הן לא קיימות
            db.create_all()
            # השם הבא מעטמא - אם תרצה להיות בלי פרטי ברירת מחדל, הסר את ה-#
            # quick_seed()  # ⬅️ כרגע זה מכובה כדי לא למחוק נתונים קיימים
            print("--- סיימתי Seed בהצלחה! ---")
        except Exception as e:
            print(f"❌ שגיאה קריטית ב-Seed: {e}")

    # הפעלת השרת ב-Debug mode כדי לראות שגיאות בצורה מפורשת
    app.run(debug=True, port=5000, host='0.0.0.0')

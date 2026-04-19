
# -*- coding: utf-8 -*-
# השורה הזו חשובה כדי שהערות בעברית לא יגרמו בעיות בקידוד

from flask_sqlalchemy import SQLAlchemy

# יצירת instance של SQLAlchemy - זה מה שיוצר את טבלאות בסיס הנתונים
db = SQLAlchemy()

# --- מחלקה בסיס לכל המודלים ---
class BaseModel(db.Model):
    """
    מחלקה בסיס שמכילה שדה ID ושיטת save משותפת.
    כל המודלים האחרים יורשים ממנה.
    """
    # ציון שזו מחלקה בסיס בלבד ולא יוצרת טבלה בעצמה
    __abstract__ = True
    
    # כל רשומה בטבלה תקבל ID ייחודי שיעלה אוטומטית
    id = db.Column(db.Integer, primary_key=True)

    def save(self):
        """
        שמירה של הרשומה לבסיס הנתונים.
        שימוש: user.save() במקום db.session.add ו-db.session.commit
        """
        db.session.add(self)
        db.session.commit()

# --- מודל המשתמש ---
class User(db.Model):
    """
    טבלת המשתמשים.
    כל משתמש בעל שם, אימייל, סיסמה מוצפנת, תפקיד והרשאות שונות.
    """
    # שם הטבלה בבסיס הנתונים
    __tablename__ = 'users'
    
    # זהה ייחודי לכל משתמש
    id = db.Column(db.Integer, primary_key=True)
    
    # שם המשתמש (עד 100 תווים, חובה)
    Name = db.Column(db.String(100), nullable=False)
    
    # כתובת אימייל (ייחודית, לא יכולה להיות כפולה, חובה)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    
    # סיסמה מוצפנת (לעולם לא שומרים סיסמה קטנה!)
    password = db.Column(db.String(120), nullable=False)
    
    # התפקיד של המשתמש: User (משתמש רגיל), ContentCreator (יוצר תוכן), Admin (מנהל)
    role = db.Column(db.String(20), default='User')
    
    # האם אושר המשתמש להעלות מתכונים
    is_approved_uploader = db.Column(db.Boolean, default=False)
    
    # האם המשתמש הוא יוצר תוכן (שדה חלופי)
    is_content_user = db.Column(db.Boolean, default=False)
    
    # האם המשתמש ממתין לאישור מנהל
    request_pending = db.Column(db.Boolean, default=False)
    
    # קשר לטבלת המתכונים (מעלי שינויתי אותו - זה יכול להישאר מעיר או להיות מופעל בעתיד)
    # recipes = db.relationship('Recipe', backref='author', lazy=True)

# --- מודל המתכון ---
class Recipe(BaseModel):
    """
    טבלת המתכונים.
    כל מתכון כולל שם, תיאור, זמן הכנה, תמונות, מרכיבים ודירוגים.
    """
    # שם הטבלה בבסיס הנתונים
    __tablename__ = 'recipes'
    
    # שם המתכון (עד 100 תווים, חובה)
    name = db.Column(db.String(100), nullable=False)
    
    # תיאור המתכון (טקסט ארוך בלי הגבלה)
    description = db.Column(db.Text)
    
    # זמן הכנת המתכון בדקות
    prepTime = db.Column(db.Integer)
    
    # סוג המתכון (בשרי, חלבי, פרווה, וגן וכו')
    type = db.Column(db.String(50))
    
    # נתיב התמונה הראשית (שם הקובץ בתיקיית uploads)
    imagePath = db.Column(db.String(255))
    
    # נתיבים של וריאציות התמונה (שחור-לבן, מסובב, טשטוש)
    # שמור כ-comma-separated string: "image_bw.jpg, image_rotated.jpg, image_blur.jpg"
    variation_paths = db.Column(db.Text)
    
    # --- שדות הדירוג ---
    # הדירוג הממוצע של המתכון (1-5)
    rating = db.Column(db.Float, default=5.0)
    
    # כמות הדירוגים שקיבל המתכון (כמה אנשים דירגו)
    rating_count = db.Column(db.Integer, default=0)
    
    # סכום כל הדירוגים (משמש לחישוב הממוצע)
    # דוגמה: אם יש 2 דירוגים של 5 ו-4, אז total_rating_sum = 9
    total_rating_sum = db.Column(db.Float, default=0.0)
    
    # הוראות הכנה (טקסט ארוך)
    instructions = db.Column(db.Text)
    
    # --- קשר למשתמש ---
    # ID של המשתמש שיצר את המתכון (קשר עם טבלת users)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # --- קשר למרכיבים ---
    # רשימה של המרכיבים של המתכון
    # backref='recipe' אומר שאפשר לכתוב ingredient.recipe כדי להגיע למתכון
    # lazy=True אומר שהמרכיבים יטענו בעת הגישה אליהם
    # cascade="all, delete-orphan" אומר: כשנמחק מתכון, גם המרכיבים שלו יימחקו
    ingredients = db.relationship('IngredientEntry', backref='recipe', lazy=True, cascade="all, delete-orphan")

# --- מודל ערך מרכיב ---
class IngredientEntry(BaseModel):
    """
    טבלת המרכיבים של כל מתכון.
    כל רשומה זה מרכיב אחד עם שם, כמות ויחידה.
    """
    # שם הטבלה בבסיס הנתונים
    __tablename__ = 'ingredients'
    
    # ID של המתכון שלו שייך המרכיב הזה (קשר עם טבלת recipes)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    
    # שם המרכיב (למשל: "בצל", "חמאה", "מלח")
    Product = db.Column(db.String(100), nullable=False)
    
    # הכמות של המרכיב (למשל: 2, 0.5, 500)
    amount = db.Column(db.Float, nullable=False)
    
    # יחידת המדידה (למשל: "יחידות", "גרם", "כוס", "כפית")
    unit = db.Column(db.String(50), nullable=False)
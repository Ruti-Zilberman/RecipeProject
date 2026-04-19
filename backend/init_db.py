# init_db.py
import os
import sys

# מוודאים שתיקיית הפרויקט נמצאת בנתיב
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# הייבוא כאן יספק לנו את app ואת db
from app import app, db

# לא צריך לייבא את models מפורשות אם app.py מייבא אותם לאחר הגדרת db!
# אבל נשאיר אותם ליתר ביטחון, ללא שינוי, כיוון שהתיקון נעשה ב-app.py
from models import *

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    
print("Initialization finished.")
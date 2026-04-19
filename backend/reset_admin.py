from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin_email = 'admin@gmail.com' 
    
    user = User.query.filter_by(Email=admin_email).first()
    
    hashed_password = generate_password_hash('123456')
    
    if user:
        user.role = 'Admin'
        user.password = hashed_password
        user.is_approved_uploader = True
        print(f"Updating existing user: {admin_email}")
    else:
        print(f"Creating new admin user: {admin_email}")
        user = User(
            Name='Admin',  # ✅ גדול N - כמו ב-models.py
            Email=admin_email,  # ✅ גדול E - כמו ב-models.py
            password=hashed_password,
            role='Admin',
            is_approved_uploader=True
        )
        db.session.add(user)
    
    db.session.commit()
    print("--- Admin password has been hashed and saved! ---")
    print(f"Email: {admin_email} | Password: 123456")
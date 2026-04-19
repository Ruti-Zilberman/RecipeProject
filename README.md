🍳 RecipeShare – Smart Recipe Sharing Platform
📌 Overview
Backend system for sharing and discovering recipes. Built with Python (Flask), SQLite (SQLAlchemy), and Angular. 
+2

🧠 Data Model

User: Stores credentials and permission roles (Admin, Uploader, Reader). 
+1


Recipe: Contains main recipe data, including original and variant image paths. 
+1


IngredientEntry: Manages quantities and units, establishing a One-to-Many relationship with recipes. 
+2


BaseModel: A foundation class providing id and save() methods to all other models. 
+1

🔒 Security Note: Access to sensitive functions is restricted via custom decorators based on user roles. 
+1

⚙️ Business Logic
Smart Ingredient Search
The core algorithm calculates a Matching Score to suggest recipes that require minimum additional shopping: 
+1


Intersection: Finds ingredients shared between the user's input and the recipe's requirements using Python's set operations. 


Score Calculation: (Shared Ingredients) / (Required Ingredients). 
+1


Ranking: Results are filtered by a threshold (e.g., 20%) and sorted in descending order by score. 

Advanced Image Gallery
Automated pipeline for image processing using the Pillow library: 
+1

Generates 3 additional variations (e.g., Black & White, Rotated, Cropped) for every uploaded photo. 

Ensures unique filenames via uuid to prevent server-side naming collisions. 
+1

🎨 Design Decision

ORM Approach: We utilize Object-Relational Mapping (OOP) instead of raw SQL queries for more maintainable and readable code. 
+1


Client-Server Separation: Images are served through dedicated GET routes, ensuring accessibility and security across different devices. 
+1

Project Documentation | Recipe Sharing Platform | Final Project

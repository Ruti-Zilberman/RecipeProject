RecipeShare – Smart Recipe Sharing & Search Platform
A comprehensive system for sharing recipes, managing advanced image galleries, and performing smart searches based on available ingredients.
+1

🚀 Technologies

Backend: Python with Flask.
+3


Database: SQLite with SQLAlchemy using an ORM approach.
+2


Frontend: Angular.
+1


Image Processing: Pillow library for automated image manipulation.
+2

🌟 Key Features

Search by Ingredients: An algorithm that calculates a matching score based on the user's available ingredients.
+2


Advanced Image Gallery: Each recipe features the original image plus three automatically generated variations (e.g., black & white, rotated, or cropped).
+2

Permission Management: Three user roles:


Regular User: Can view, search, and rate recipes.
+1


Content Uploader: A regular user authorized to add recipes to the database.
+1


Admin: Can delete recipes, upload content, and approve uploader requests.
+2


Filtering & Sorting: Ability to filter by kosher status (Dairy, Meat, Parve), preparation time, and rating.
+1

🛠 Data Models (ORM)
The project utilizes inheritance from a BaseModel which provides an id and a save() method:
+2


User: Stores credentials (password), roles, and the is_approved_uploader flag.
+3


Recipe: Stores main recipe data, the original image_path, and a variation_paths string/JSON for generated images.
+2


IngredientEntry: Manages quantities and units, creating a One-to-Many relationship between recipes and their ingredients.
+2

🧠 Search Algorithm
The server processes searches in four main steps:
+1


Data Preparation: User and recipe ingredient lists are converted into Sets.
+1


Intersection: Finds matching ingredients using the & operator.
+1


Matching Score: Calculated as: 
Required Ingredients Count
Shared Ingredients Count
​
 
.
+1


Sorting: Results are filtered by a minimum threshold and sorted in descending order by score.
+1

🖼 Image Handling Pipeline
When an image is uploaded via POST /upload:
+1


Unique Naming: The server generates a unique filename using uuid4 to prevent conflicts.
+2


Storage: The original file is saved in the /uploads/ directory on the server.
+1


Variations: Pillow generates three additional files (e.g., img.convert('L') for B&W).
+1


DB Update: Paths for all four images are saved in the recipe record.
+1


Display: The client retrieves images via a separate GET request using the saved URLs.
+1

🔒 Security

Decorators: Used on the server to verify permissions for sensitive functions.
+2


Server-Side Validation: Ensures that only authorized users can perform specific actions like deleting recipes or approving uploaders.
+1


Error Handling: The server is configured to return appropriate errors for unauthorized access.
+1

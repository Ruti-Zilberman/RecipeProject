# RecipeShare – Smart Recipe Sharing & Search Platform

[cite_start]A comprehensive system for sharing recipes, managing advanced image galleries, and performing smart searches based on available ingredients[cite: 331, 419].

---

### 🚀 Technologies
* [cite_start]**Backend:** Python with Flask[cite: 339, 427].
* [cite_start]**Database:** SQLite with SQLAlchemy using an ORM approach[cite: 339, 427, 449].
* [cite_start]**Frontend:** Angular[cite: 340, 429].
* [cite_start]**Image Processing:** Pillow library for automated image manipulation[cite: 393, 487].

---

### 🌟 Key Features
* [cite_start]**Search by Ingredients:** An algorithm that calculates a matching score based on the user's available ingredients[cite: 334, 422].
* [cite_start]**Advanced Image Gallery:** Each recipe features the original image plus three automatically generated variations (e.g., black & white, rotated, or cropped)[cite: 336, 424].
* [cite_start]**Permission Management:** Three user roles[cite: 342, 431]:
    * [cite_start]**Regular User:** Can view, search, and rate recipes[cite: 344, 433].
    * [cite_start]**Content Uploader:** A regular user authorized to add recipes to the database[cite: 345, 434].
    * [cite_start]**Admin:** Can delete recipes, upload content, and approve uploader requests[cite: 347, 436].
* [cite_start]**Filtering & Sorting:** Ability to filter by category (Dairy, Meat, Parve), preparation time, and rating[cite: 353, 441].

---

### 🛠 Data Models (ORM)
[cite_start]The project utilizes inheritance from a `BaseModel` which provides an `id` and a `save()` method[cite: 367, 455]:
* [cite_start]**User:** Stores credentials (password), roles, and the `is_approved_uploader` flag[cite: 367, 369, 455, 457].
* [cite_start]**Recipe:** Stores main recipe data, the original `image_path`, and a `variation_paths` string/JSON for generated images[cite: 367, 369, 455, 457].
* [cite_start]**IngredientEntry:** Manages quantities and units, creating a One-to-Many relationship between recipes and their ingredients[cite: 367, 369, 455, 457].

---

### 🧠 Search Algorithm
[cite_start]The server processes searches in four main steps[cite: 375, 467]:
1.  [cite_start]**Data Preparation:** User and recipe ingredient lists are converted into **Sets**[cite: 377, 469].
2.  [cite_start]**Intersection:** Finds matching ingredients using the `&` operator[cite: 379, 471].
3.  [cite_start]**Matching Score:** Calculated as: (Shared Ingredients Count / Required Ingredients Count)[cite: 383, 476].
4.  [cite_start]**Sorting:** Results are filtered by a minimum threshold and sorted in descending order by score[cite: 388, 480].

---

### 🖼 Image Handling Pipeline
[cite_start]When an image is uploaded via `POST /upload`[cite: 266, 313]:
1.  [cite_start]**Unique Naming:** The server generates a unique filename using `uuid4` to prevent conflicts[cite: 289, 399, 497].
2.  [cite_start]**Storage:** The original file is saved in the `/uploads/` directory on the server[cite: 271, 290, 493].
3.  [cite_start]**Variations:** Pillow generates three additional files (e.g., black & white, rotated, or cropped)[cite: 394, 395, 488, 492].
4.  [cite_start]**DB Update:** Paths for all four images are saved in the recipe record[cite: 396, 494].
5.  [cite_start]**Display:** The client retrieves images via a separate `GET` request using the saved URLs[cite: 279, 294, 321].

---

### 🔒 Security
* [cite_start]**Decorators:** Used on the server to verify permissions for sensitive functions[cite: 369, 410, 457, 508].
* [cite_start]**Server-Side Validation:** Ensures that only authorized users can perform specific actions like deleting recipes or approving uploaders[cite: 410, 508].
* [cite_start]**Error Handling:** The server is configured to return appropriate errors for unauthorized access[cite: 411, 509].

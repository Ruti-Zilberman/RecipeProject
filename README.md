# 🍳 RecipeShare – Smart Recipe Sharing Platform

### 📌 Overview
A professional backend system for sharing and discovering recipes. Built with a modern tech stack to ensure speed, security, and a great user experience.

---

### 🚀 Tech Stack
* **Backend:** Python & Flask
* **Database:** SQLite with SQLAlchemy (ORM)
* **Frontend:** Angular
* **Processing:** Pillow Library

---

### 🧠 Key Smart Features

#### **1. Smart Ingredient Search**
The core algorithm calculates a **Matching Score** to suggest recipes based on what you already have in your pantry:
* **Logic:** Uses Python `sets` to find the intersection between your ingredients and the recipe.
* **Ranking:** Sorted by percentage match, so the best options appear first.

#### **2. Advanced Image Gallery**
Automated image processing pipeline:
* **Auto-Generation:** Every upload creates **3 additional variations** (B&W, Rotated, etc.).
* **Security:** Unique naming via `UUID` to prevent file overrides.

---

### 🛠 Architecture & Design
* **ORM Approach:** Using Object-Oriented patterns for database management instead of raw SQL.
* **Role-Based Access:** Built-in security decorators to manage **Admin**, **Uploader**, and **Reader** permissions.
* **Clean API:** Structured routes for both data fetching and media streaming.

---
*Project Documentation | Recipe Sharing Platform | Final Project*

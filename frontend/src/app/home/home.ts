
import { Router, RouterModule } from '@angular/router';
import { RecipeService } from '../services/recipe.service';
import { FormsModule } from '@angular/forms'; // 1. ייבוא המודול של הטפסים
import { CommonModule } from '@angular/common'; // 2. ייבוא מודול בסיסי לאנגולר
import { Component, OnInit } from '@angular/core';
@Component({
  selector: 'app-home',
  standalone: true, // ודאי שזה מוגדר כ-standalone
  imports: [FormsModule, CommonModule, RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class HomeComponent implements OnInit {
  searchTerm: string = ''; // מחזיק את מה שהמשתמש מקליד בתיבת החיפוש
  featuredRecipes: any[] = []; // מערך שיכיל את 3 המתכונים להצגה בדף הבית
  constructor(private recipeService: RecipeService, private router: Router) { }

  ngOnInit() {
    // // שליפת כל המתכונים מהשרת בעת טעינת הדף
    // this.recipeService.getRecipes().subscribe({
    //   next: (data) => {
    //   // אנחנו לוקחים את כל המערך (data) והופכים אותו (reverse)
    //   // כך שהאינדקס האחרון בבסיס הנתונים הופך להיות הראשון בתצוגה
    //     this.featuredRecipes = [...data].reverse();
    //   },
    //   error: (err) => console.error('Error fetching recipes:', err)
    // });
  }


  // פונקציה לביצוע חיפוש ומעבר לדף המתכונים
  onSearch() {
    const term = this.searchTerm ? this.searchTerm.trim() : '';
    // ניווט לדף המתכונים עם "פרמטר שאילתה" (Query Parameter)
    // זה מאפשר לדף המתכונים לדעת מה חיפשנו דרך הכתובת (URL)
    this.router.navigate(['/recipes'], { queryParams: { search: term } });
  }
  // פונקציית עזר לטיפול בנתיבי תמונות
  getRecipeImage(imagePath: string): string {
    if (!imagePath) return 'assets/default-recipe.jpg'; // תמונת ברירת מחדל
    if (imagePath.startsWith('http')) return imagePath; // אם זה נתיב חיצוני מלא
    return `http://localhost:5000/${imagePath}`; // חיבור לנתיב של שרת הפייתון
  }
  // מעבר לדף המתכונים ללא סינון (צפייה בכל הקטלוג)
  onBrowseAll() {
    this.router.navigate(['/recipes']);
  }

}

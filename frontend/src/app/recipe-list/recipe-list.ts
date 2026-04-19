import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { RecipeService } from '../services/recipe.service';
import { Recipe } from '../recipe.model'; 
import { FormsModule } from '@angular/forms'; 
import { ActivatedRoute } from '@angular/router';


@Component({
  selector: 'app-recipe-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './recipe-list.html',
  styleUrl: './recipe-list.css'
})
export class RecipeListComponent implements OnInit {
  // --- הגדרת משתנים ---
  recipes: Recipe[] = [];           // המערך המקורי שמגיע מהשרת (המקור האמין)
  allRecipes: any[] = [];           
  filteredRecipes: Recipe[] = [];   // המערך שמוצג בפועל למשתמש (אחרי פילטרים)
  searchTerm: string = '';          // מילת החיפוש שהגיעה מהדף הקודם (מצרכים)
  localSearchName: string = '';     // חיפוש חופשי בשם המתכון בתוך הדף הנוכחי
  maxTime: number = 180;            // זמן הכנה מקסימלי (לפי הסליידר)
  selectedCategory: string = '';    // קטגוריה שנבחרה
  sortBy: string = 'score';         // סוג המיון (לפי התאמה או זמן)
  isNumericSearch: boolean = false;
  isLoading: boolean = false;       // אינדיקטור להצגת מצב טעינה
  selectedType: string = '';        // סוג מנה (בשרי/חלבי/פרווה)

  constructor(public recipeService: RecipeService, private route: ActivatedRoute) { }

ngOnInit(): void {
  // האזנה לשינויים בפרמטרים של הכתובת (URL)
  this.route.queryParams.subscribe(params => {
    const term = params['search'];

    if (term && term.trim() !== '') {
      // 1. הגדרות ראשוניות לחיפוש
      this.searchTerm = term;
      this.isLoading = true;
      this.maxTime = 180; // איפוס הזמן למקסימום כדי שלא יסנן תוצאות בטעות
      this.localSearchName = ''; // איפוס חיפוש פנימי

      // 2. קריאה לשרת לחיפוש לפי מצרכים
      this.recipeService.searchRecipesByIngredients(term).subscribe({
        next: (data) => {
          console.log('נתונים שהתקבלו מהחיפוש בדף הבית:', data);
          this.recipes = data;         // שמירת ה-18 מתכונים שראינו ב-Console
          this.applyLocalFilters();    // הפעלת הפילטר להצגה במסך
          this.isLoading = false;
        },
        error: (err) => {
          console.error('שגיאה בחיפוש:', err);
          this.isLoading = false;
        }
      });
    } else {
      // אם אין חיפוש ב-URL, טוענים את הכל כרגיל
      this.searchTerm = '';
      this.loadRecipes();
    }
  });

  // האזנה לקטגוריות ומיון מה-Navbar
  this.recipeService.categoryState$.subscribe(cat => {
    this.selectedCategory = cat;
    this.applyLocalFilters();
  });

  this.recipeService.sortState$.subscribe(sort => {
    this.sortBy = sort;
    this.applyLocalFilters();
  });
}
  // הצגת תמונת ברירת מחדל אם התמונה מהשרת נכשלת בטעינה
  updateDefaultImage(event: any) {
    event.target.src = 'assets/default-recipe.jpg';
  }

  // טעינת כל המתכונים הקיימים מהשרת
  loadRecipes() {
    this.recipeService.getRecipes().subscribe((data) => {
      this.recipes = data;
      this.filteredRecipes = data; 
      console.log('מתכונים נטענו:', this.filteredRecipes);
    });
  }

  // פונקציית חיפוש לפי מצרכים (מופעלת ידנית אם צריך)
  searchRecipesByIngredients(term: string): void {
    this.recipeService.searchRecipesByIngredients(term).subscribe({
      next: (results: Recipe[]) => {
        this.recipes = results;
        this.applyLocalFilters(); 
      },
      error: (err) => {
        console.error('שגיאה בחיפוש:', err);
        this.recipes = [];
        this.applyLocalFilters();
      }
    });
  }

  // דירוג מתכון בכוכבים
  rateRecipe(recipeId: number, stars: number): void {
    // עדכון אופטימי - שינוי התצוגה מיד כדי שהמשתמש יקבל משוב מהיר
    const recipe = this.recipes.find(r => r.id === recipeId);
    if (recipe) {
      recipe.rating = stars;
    }

    // שליחה לשרת ושמירה קבועה
    this.recipeService.rateRecipe(recipeId, stars).subscribe({
      next: (response: any) => {
        // עדכון הממוצע האמיתי כפי שהתקבל מהשרת
        if (recipe && response.new_average) {
          recipe.rating = response.new_average;
        }
      },
      error: (err) => console.error('Error rating:', err)
    });
  }

  // מחיקת מתכון (למי שיכול)
  deleteRecipe(id: number): void {
    if (confirm('האם את בטוחה שברצונך למחוק את המתכון?')) {
      this.recipeService.deleteRecipe(id).subscribe(() => {
        // רענון הרשימה לאחר מחיקה
        if (this.searchTerm.trim()) {
          this.searchRecipesByIngredients(this.searchTerm);
        } else {
          this.loadRecipes();
        }
      });
    }
  }
applyLocalFilters(): void {
  console.log('מפעיל פילטרים על:', this.recipes.length, 'מתכונים');
  if (!this.recipes || this.recipes.length === 0) {
    this.filteredRecipes = [];
    return;
  }

  this.filteredRecipes = this.recipes.filter(r => {
    // וידוא שהשדות קיימים כדי למנוע שגיאות
    const rName = r.name ? r.name.toLowerCase() : '';
    const rType = r.type ? r.type.toLowerCase() : '';
    const rTime = Number(r.prepTime) || 0;

    const matchesName = rName.includes(this.localSearchName.toLowerCase());
    
    // סינון לפי זמן - ודאי ש-maxTime לא קטן מדי
    const matchesTime = rTime <= this.maxTime;
    
    // סינון לפי סוג - אם לא נבחר סוג, הכל עובר
    const matchesType = !this.selectedType || rType === this.selectedType.toLowerCase();

    return matchesName && matchesTime && matchesType;
  });

  this.sortResults();
}
  // // ---  סינון המתכונים על המסך ---
  // applyLocalFilters(): void {
  //   if (!this.recipes) {
  //     this.filteredRecipes = [];
  //     return;
  //   }

  //   this.filteredRecipes = this.recipes.filter(r => {
  //     // סינון 1: לפי שם המתכון (התעלמות מאותיות גדולות/קטנות)
  //     const matchesName = (r.name || '').toLowerCase().includes(this.localSearchName.toLowerCase());
      
  //     // סינון 2: לפי זמן הכנה (מראה רק מה שקצר מהזמן שנבחר)
  //     const matchesTime = Number(r.prepTime || 0) <= this.maxTime;
      
  //     // סינון 3: לפי סוג (בשרי/חלבי/פרווה)
  //     const matchesType = !this.selectedType || 
  //                         (r.type || '').toLowerCase() === this.selectedType.toLowerCase();

  //     return matchesName && matchesTime && matchesType;
  //   });

  //   // לאחר הסינון - מפעיל את פונקציית המיון
  //   this.sortResults();
  // }

  // מיון התוצאות לפי בחירת המשתמש
  sortResults(): void {
    if (this.sortBy === 'score') {
      // מיון לפי אחוז התאמה למצרכים (מהגבוה לנמוך)
      this.filteredRecipes.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
    } else if (this.sortBy === 'time') {
      // מיון לפי זמן הכנה (מהקצר לארוך)
      this.filteredRecipes.sort((a, b) => (Number(a.prepTime) || 0) - (Number(b.prepTime) || 0));
    }
  }

  // איפוס כל הפילטרים וחזרה למצב ברירת מחדל
  clearFilters(): void {
    this.localSearchName = ''; 
    this.maxTime = 180;           
    this.selectedCategory = '';  
    this.sortBy = 'score';        
    this.applyLocalFilters();    
  }

  // בניית נתיב התמונה לשרת ה-Flask
  getRecipeImage(imagePath: string | undefined): string {
    if (!imagePath) return 'assets/default-recipe.jpg';
    if (imagePath.startsWith('http')) return imagePath;
    return `http://localhost:5000/${imagePath}`;
  }

  // טיפול מתקדם בנתיבי תמונות (תיקון אוטומטי של נתיבים חסרים/שגויים)
  getImageUrl(imagePath: string | undefined | null): string {
    if (!imagePath) return 'assets/images/default-recipe.jpg';
    if (imagePath.startsWith('http') && imagePath.includes('static/uploads')) return imagePath;
    if (imagePath.startsWith('http') && !imagePath.includes('static/uploads')) {
      const fileName = imagePath.split('/').pop();
      return `http://localhost:5000/static/uploads/${fileName}`;
    }
    return `http://localhost:5000/static/uploads/${imagePath}`;
  }

  // החזרת מחלקת עיצוב (CSS) לפי ציון ההתאמה
  getScoreClass(score: number): string {
    if (score >= 80) return 'score-high';   // ירוק
    if (score >= 50) return 'score-medium'; // כתום
    return 'score-low';                     // אדום
  }
}
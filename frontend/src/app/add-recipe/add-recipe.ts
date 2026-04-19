
// ============================================
// יבואים - ספריות מ-Angular ו-HttpClient
// ============================================
import { Component, OnInit } from '@angular/core'; // קומפוננט Angular עם lifecycle hooks
import { CommonModule } from '@angular/common';  // לתבניות כמו *ngIf ו-*ngFor
import { FormsModule } from '@angular/forms';  // two-way binding עם [(ngModel)]
import { HttpClient } from '@angular/common/http';  // בקשות HTTP לשרת
import { Router, ActivatedRoute } from '@angular/router'; // ניווט וקבלת פרמטרים מ-URL

// ============================================
// קומפוננט - הגדרות הקומפוננט
// ============================================
@Component({
  selector: 'app-add-recipe',  // השם של הקומפוננט ב-HTML
  standalone: true,  // קומפוננט עצמאי (Standalone) ללא module
  imports: [CommonModule, FormsModule],  // ספריות שהקומפוננט משתמש בהן
  templateUrl: './add-recipe.html',  // הקובץ HTML של הטמפלייט
  styleUrl: './add-recipe.css'  // הקובץ CSS לעיצוב
})
export class AddRecipeComponent implements OnInit {
  // ============================================
  // משתנים בקומפוננט - נתוני הטופס
  // ============================================
  
  // אובייקט מתכון חדש שמתחיל ריק
  newRecipe = {
    title: '',  // שם המתכון
    description: '',  // הסבר על המתכון
    instructions: '',  // הוראות ההכנה
    prepTime: 0,  // זמן הכנה בדקות
    type: 'פרווה',  // דור המתכון (פרווה/חלבי/בשרי)
    rating: 5,  // דירוג של המתכון
    ingredients: [{ name: '', amount: '1', unit: 'יחידה' }]  // רשימת מרכיבים עם יחידות
  };

  selectedFile: File | null = null;  // התמונה שנבחרה עבור המתכון
  errorMessage: string = '';  // הודעת שגיאה להצגה בתשובה
  
  // משתנים חדשים לעריכה
  isEditMode = false;  // בדיקה אם אנחנו בעריכה או יצירה חדשה
  recipeId: number | null = null;  // ID של המתכון שמעדכנים (אם בעריכה)

  // ============================================
  // Constructor - הזרקת Dependencies
  // ============================================
  constructor(
    private http: HttpClient,  // לשליחת בקשות HTTP לשרת
    private router: Router,  // לנווט בין עמודים
    private route: ActivatedRoute  // קבלת פרמטרים מה-URL (למשל: /add-recipe?id=5)
  ) {}

  // ============================================
  // lifecycle hook - טוען נתונים בהצגה הראשונה
  // ============================================
  ngOnInit() {
    // בדיקה אם קיבלנו ID בכתובת ה-URL (למשל: /add-recipe?id=5)
    this.route.queryParams.subscribe(params => {
      if (params['id']) {  // אם יש ID - זה עריכה של מתכון קיים
        this.recipeId = +params['id'];  // המרת ID למספר
        this.isEditMode = true;  // סימון שאנחנו במצב עריכה
        this.loadRecipeData(this.recipeId);  // טעינת נתוני המתכון מהשרת
      }
    });
  }

  // ============================================
  // פונקציה שטוענת את נתוני המתכון הקיים לתוך הטופס
  // ============================================
  loadRecipeData(id: number) {
    // שליחת בקשה לשרת לשליפת נתוני המתכון
    this.http.get<any>(`http://localhost:5000/api/recipes/${id}`).subscribe({
      next: (recipe) => {
        // עדכון האובייקט גורם לטופס להתמלא אוטומטית בזכות ה-Two-way binding
        this.newRecipe = {
          title: recipe.name || recipe.title,  // שם המתכון בשרת הוא 'name' אבל בטופס הוא 'title'
          description: recipe.description,  // הסבר על המתכון
          instructions: recipe.instructions,  // הוראות ההכנה
          prepTime: recipe.prepTime,  // זמן הכנה
          type: recipe.type,  // סוג המתכון
          rating: recipe.rating || 5,  // דירוג ברירת מחדל אם לא קיים בשרת
          ingredients: recipe.ingredients  // מקבל רשימה של מרכיבים שעברו עיבוד בשרת
        };
        console.log('הנתונים נטענו בהצלחה:', this.newRecipe);  // הדפסה לקונסול כדי לבדוק את הנתונים
      },
      error: (err) => {
        // אם יש שגיאה בטעינה - הודעה למשתמש
        console.error('שגיאה בטעינת נתוני המתכון:', err);
        alert('לא הצלחנו לטעון את נתוני המתכון לעריכה.');
      }
    });
  }

  // ============================================
  // פונקציה - בחירת תמונה מהמחשב
  // ============================================
  onFileSelected(event: any) {
    // בדיקה אם המשתמש בחר קובץ
    if (event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];  // שמירה של הקובץ המנוחר בזיכרון
    }
  }

  // ============================================
  // פונקציה - הוספת שורה חדשה למרכיב
  // ============================================
  addIngredient() {
    // הוספה של שורה חדשה לרשימת המרכיבים
    this.newRecipe.ingredients.push({ name: '', amount: '1', unit: 'יחידה' });
  }

  // ============================================
  // פונקציה - הסרה של שורה של מרכיב
  // ============================================
  removeIngredient(index: number) {
    // בדיקה שנשאר לפחות מרכיב אחד
    if (this.newRecipe.ingredients.length > 1) {
      this.newRecipe.ingredients.splice(index, 1);  // הסרה של המרכיב מהרשימה
    }
  }

  // ============================================
  // פונקציה מאוחדת - שמירה או עדכון מתכון
  // ============================================
  createRecipe() {
    // קבלת דוא"ל של המשתמש המחובר מהזיכרון
    const userEmail = localStorage.getItem('userEmail');
    
    // אם אין דוא"ל - המשתמש לא מחובר
    if (!userEmail) {
      this.errorMessage = 'עליך להיות מחובר כדי לבצע פעולה זו';
      return;
    }

    // יצירת FormData לשליחת קבצים וטקסט
    const formData = new FormData();
    
    // הוספת כל השדות לטופס שליחה
    formData.append('title', this.newRecipe.title);  // שם המתכון
    formData.append('description', this.newRecipe.description);  // הסבר
    formData.append('instructions', this.newRecipe.instructions);  // הוראות
    formData.append('prepTime', this.newRecipe.prepTime.toString());  // זמן הכנה
    formData.append('type', this.newRecipe.type);  // סוג המתכון
    formData.append('email', userEmail);  // דוא"ל המשתמש
    
    // המרה של מערך מרכיבים ל-JSON string
    formData.append('ingredients', JSON.stringify(this.newRecipe.ingredients));

    // אם נבחרה תמונה - הוספתה לשליחה
    if (this.selectedFile) {
      formData.append('image', this.selectedFile);
    }

    // בדיקה אם אנחנו במצב עריכה או יצירה חדשה
    if (this.isEditMode && this.recipeId) {
      // אם אנחנו במצב עריכה - שליחת PUT לעדכון המתכון הקיים
      this.http.put(`http://localhost:5000/api/recipes/${this.recipeId}`, formData).subscribe({
        next: () => {  // אם ההשליחה הצליחה
          alert('המתכון עודכן בהצלחה!');
          this.router.navigate(['/profile']);  // ניווט לעמוד הפרופיל
        },
        error: (err) => this.handleError(err)  // טיפול בשגיאה
      });
    } else {
      // אם אנחנו במצב יצירה - שליחת POST למתכון חדש (כפי שהיה לך)
      this.http.post('http://localhost:5000/recipes/create', formData).subscribe({
        next: () => {  // אם ההשליחה הצליחה
          alert('המתכון נוצר בהצלחה!');
          this.router.navigate(['/profile']);  // ניווט לעמוד הפרופיל
        },
        error: (err) => this.handleError(err)  // טיפול בשגיאה
      });
    }
  }

  // ============================================
  // פונקציה - טיפול בשגיאות
  // ============================================
  handleError(err: any) {
    // הדפסה של השגיאה לקונסול לצורך ניפוי באגים
    console.error('שגיאה:', err);
    // הצגת הודעת שגיאה כללית למשתמש
    this.errorMessage = 'אופס! משהו השתבש בניסיון לשמור את המתכון.';
  }
}
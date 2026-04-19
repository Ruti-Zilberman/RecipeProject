import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RecipeService } from '../services/recipe.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginComponent {
  // אובייקט לאיסוף נתוני ההתחברות מהטופס
  loginData = {
    email: '',
    password: ''
  };

  constructor(
    private http: HttpClient, 
    private router: Router,
    private recipeService: RecipeService 
  ) {}
onLogin() {
// שליחת בקשת POST לשרת הפייתון עם פרטי המשתמש (אימייל וסיסמה)
  this.http.post('http://localhost:5000/login', this.loginData)
  .subscribe({
    next: (response: any) => {
        // --- שלב 1: שמירת נתונים מקומית ---
        // שמירת הנתונים בדפדפן כדי שהמשתמש יישאר מחובר גם אחרי רענון
      localStorage.setItem('userEmail', response.email);
      localStorage.setItem('userRole', response.role);
      
      // בחירת השם להצגה (טיפול בשמות משתנים שונים שחוזרים מה-API)
      const nameToShow = response.userName || response.name || 'אורח';
      // --- שלב 2: עדכון מערכת ה-State (ה-Service) ---
        // מעדכן את ה-Service שהתבצעה התחברות מוצלחת
      this.recipeService.setLoggedIn(true, nameToShow, response.role);
      // עדכון אובייקט המשתמש המלא כדי שכל האתר (וה-Navbar) יתעדכנו מיד
        this.recipeService.updateUser(response);
      alert('התחברת בהצלחה! ברוך הבא ' + nameToShow);
      // --- שלב 3: ניתוב ---
       // מעבר לדף המתכונים הראשי
      this.router.navigate(['/recipes']);
    },
    error: (err) => {
      // טיפול במקרה של פרטים שגויים או שגיאת שרת
      console.error('Login error:', err);
      alert('שגיאה בהתחברות: ' + (err.error?.message || 'אימייל או סיסמה שגויים'));
    }
  });
}
}
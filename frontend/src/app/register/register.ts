import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RecipeService } from '../services/recipe.service';
@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterModule, CommonModule],
  templateUrl: './register.html',
  styleUrls: ['./register.css']
})
export class RegisterComponent {
  // האובייקט שמחזיק את הנתונים מה-HTML
  registerData = { name: '', email: '', password: '' };
  errorMessage: string = '';
  constructor(private http: HttpClient, private router: Router, public recipeService: RecipeService) { }
// פונקציה המופעלת בעת לחיצה על כפתור ההרשמה
  onRegister() {
    console.log('מנסה להירשם עם:', this.registerData);
// ביצוע קריאת POST לשרת הפייתון עם נתוני המשתמש
    this.http.post('http://localhost:5000/register', this.registerData).subscribe({
      next: (response: any) => {
       // --- שלב 1: סנכרון מצב המשתמש ---
       // עדכון ה-Service כדי שה-Navbar יציג "שלום" וכפתורי ניהול מיד
        const nameToShow = response.userName || response.name || 'משתמש חדש';
        this.recipeService.updateUser(response);
        this.recipeService.setLoggedIn(true, nameToShow, response.role || 'User');

        // --- שלב 2: שמירת מידע בדפדפן ---
        // שמירה ב-LocalStorage כדי שהחיבור יישאר גם לאחר רענון הדף
        localStorage.setItem('userEmail', response.email);
        localStorage.setItem('userRole', response.role || 'User');
        localStorage.setItem('userName', response.userName || response.name);


        alert('הרישום הצליח! ברוך הבא ' + nameToShow);
        // --- שלב 3: ניתוב ---       
        // מעבר אוטומטי לדף המתכונים לאחר הרשמה מוצלחת
        this.router.navigate(['/recipes']);
      },
      error: (err) => {
        console.error(err);
        this.errorMessage = err.error?.message || 'שגיאה בתקשורת עם השרת';
        alert('שגיאה ברישום: ' + this.errorMessage);
      }
    });
  }
}
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RecipeService } from '../services/recipe.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.css',
})
export class AdminDashboardComponent implements OnInit {
// --- משתני מחלקה ---
  users: any[] = []; // מערך שיחזיק את כל המשתמשים שנקבל מהשרת
  adminEmail: string | null = ''; // המייל של המנהל הנוכחי לצורך הרשאות

  constructor(private recipeService: RecipeService) { }

  ngOnInit() {
    this.adminEmail = localStorage.getItem('userEmail');
    this.loadUsers();
  }

  
  // טעינת רשימת המשתמשים מהשרת
  loadUsers() {
    // אבטחה: מוודאים שיש לנו את המייל של המנהל לפני שפונים לשרת
    const email = localStorage.getItem('userEmail') || JSON.parse(localStorage.getItem('user') || '{}').Email;
    if (email) {
      this.adminEmail = email;
      console.log('שולח בקשה עם מייל:', email); // בדקי שזה מדפיס admin@gmail.com
      // פנייה ל-Service לקבלת כל המשתמשים. השרת בודק אם ה-Email הזה הוא אכן מנהל
      this.recipeService.getAllUsers(email).subscribe({
        next: (data: any) => {
          this.users = data;
          console.log('המשתמשים התקבלו:', data);
        },
        error: (err) => {
          console.error('שגיאה מהשרת:', err);
          // אם עדיין יש שגיאה, נסי לראות ב-Network אם ה-Header באמת מופיע שם
        }
      });
    } else {
      console.error('לא נמצא מייל ב-LocalStorage! בצעי Login מחדש.');
    }
  }



  // אישור משתמש
  onApprove(userId: number) {
    if (this.adminEmail) {
      // קריאה לשרת עם המייל של המנהל וה-ID של המשתמש שרוצים לאשר
      this.recipeService.approveUser(this.adminEmail, userId).subscribe({
        next: (response: any) => { 
          alert('המשתמש אושר בהצלחה!');
          this.loadUsers();// רענון הרשימה כדי לראות את השינוי בסטטוס
        },
        error: (err: any) => { 
          alert('שגיאה באישור המשתמש');
        }
      });
    }
  }

  // מחיקת משתמש
  deleteUser(userId: number) {
      // הצגת הודעת אישור (Confirm) לפני פעולה בלתי הפיכה
    if (confirm('האם את בטוחה שברצונך למחוק משתמש זה?') && this.adminEmail) {
// שימוש בפונקציה ייעודית למנהלים למחיקת משתמשים אחרים
      this.recipeService.deleteUserFromAdmin(this.adminEmail, userId).subscribe({
        next: (response: any) => {
          alert('המשתמש נמחק בהצלחה');
          this.loadUsers();
        },
        error: (err: any) => {
          console.error(err);
          alert('שגיאה במחיקת המשתמש');
        }
      });
    }
  }
}
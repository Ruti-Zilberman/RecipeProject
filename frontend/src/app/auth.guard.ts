import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { RecipeService } from './services/recipe.service';
import { map, take } from 'rxjs';

export const authGuard = () => {
  const router = inject(Router);
  const userRole = localStorage.getItem('userRole'); // שליפת התפקיד מהאחסון
  const isLoggedIn = !!localStorage.getItem('userEmail');

  // 1. אם המשתמש בכלל לא מחובר
  if (!isLoggedIn) {
    router.navigate(['/login']);
    return false;
  }

  // 2. בדיקת הרשאות ספציפיות להוספת תוכן
  // רק אדמין או יוצר תוכן (ContentCreator) רשאים להיכנס
  if (userRole === 'Admin' || userRole === 'ContentCreator') {
    return true;
  }

  // 3. אם הוא מחובר אבל אין לו הרשאת כתיבה
  alert('אין לך הרשאה להוסיף מתכונים. בקשי מהמנהל אישור "משתמש תוכן".');
  router.navigate(['/recipes']);
  return false;
};
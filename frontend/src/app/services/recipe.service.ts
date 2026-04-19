import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { Recipe } from '../recipe.model';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class RecipeService {
  private apiUrl = 'http://localhost:5000/recipes';

  //יצירת אישור אבטחה (Header) המכיל את אימייל המנהל עבור פעולות רגישות
private getAdminHeaders(adminEmail: string): HttpHeaders {
  return new HttpHeaders({
    'Admin-Email': adminEmail 
  });
}
// ניהול תוצאות החיפוש כך שיהיו זמינות לכל הקומפוננטות באתר
  private searchResultsSource = new BehaviorSubject<Recipe[]>([]);
  currentSearchResults$ = this.searchResultsSource.asObservable();
// ניהול מצב המשתמש המחובר ושליפתו מהזיכרון המקומי (LocalStorage)
  private userSubject = new BehaviorSubject<any>(this.getUserFromStorage());
  user$ = this.userSubject.asObservable();
// משדר המציין האם המשתמש מחובר כרגע
  private loggedIn = new BehaviorSubject<boolean>(!!localStorage.getItem('userEmail')); 
  isLoggedIn$ = this.loggedIn.asObservable();
// שמירת שם המשתמש הנוכחי להצגה בתפריט
  private userName = new BehaviorSubject<string>(localStorage.getItem('userName') || '');
  userName$ = this.userName.asObservable();
// בדיקה ושידור האם המשתמש הנוכחי הוא מנהל (Admin)
  private isAdminSubject = new BehaviorSubject<boolean>(localStorage.getItem('userRole') === 'Admin');
  public isAdmin$ = this.isAdminSubject.asObservable();
// משתנים לניהול מצב החיפוש, הסינון והמיון באתר
  private searchSubject = new BehaviorSubject<string>(''); 
  searchState$ = this.searchSubject.asObservable(); 

  private categorySubject = new BehaviorSubject<string>('');
  categoryState$ = this.categorySubject.asObservable();

  private sortSubject = new BehaviorSubject<string>('score'); 
  sortState$ = this.sortSubject.asObservable();

  constructor(private http: HttpClient) { }
// פונקציות לעדכון מצבי החיפוש והסינון מתוך המסכים השונים
  updateSearchTerm(term: string) { this.searchSubject.next(term); }
  updateCategory(category: string) { this.categorySubject.next(category); }
  updateSort(sortBy: string) { this.sortSubject.next(sortBy); }
// שליפת נתוני המשתמש שנשמרו בדפדפן (כדי שלא יצטרך להתחבר מחדש ברענון)
  private getUserFromStorage() {
    const userJson = localStorage.getItem('user');
    return userJson ? JSON.parse(userJson) : null;
  }
// עדכון אובייקט המשתמש בזיכרון המקומי ובמשדר (Subject)
  updateUser(user: any) {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('userEmail', user.email || '');
    } else {
      localStorage.removeItem('user');
      localStorage.removeItem('userEmail');
    }
    this.userSubject.next(user);
    this.loggedIn.next(!!user);
  }
// עדכון סטטוס התחברות מלא, כולל שם ותפקיד, וניקוי הזיכרון בהתנתקות
  setLoggedIn(status: boolean, name: string = '', role: string = 'User') {
    this.loggedIn.next(status);
    this.userName.next(name);
    this.isAdminSubject.next(role === 'Admin');

    if (status) {
      localStorage.setItem('userName', name);
      localStorage.setItem('userRole', role);
    } else {
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      localStorage.removeItem('userRole');
      localStorage.removeItem('user'); // הוספתי
      this.updateUser(null);
    }
  }
  // פונקציה מרכזית להתנתקות - מנקה את הזיכרון ומעדכנת את כל האתר
logout() {
  // 1. הסרת כל המידע שנשמר בדפדפן
  localStorage.removeItem('user');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userName');
  localStorage.removeItem('userRole');

  // 2. עדכון ה"משדרים" (Subjects) לערכים ריקים כדי שה-UI יתעדכן מיד
  this.userSubject.next(null);
  this.loggedIn.next(false);
  this.userName.next('');
  this.isAdminSubject.next(false);

  // 3. איפוס מצבי חיפוש (כדי שהחיפוש הבא יתחיל נקי)
  this.updateSearchTerm('');
  this.updateCategory('');
}
// שליחת רשימת מרכיבים לשרת (POST) וקבלת מתכונים מתאימים עם ציון התאמה
  searchRecipesByIngredients(term: string): Observable<Recipe[]> {
    return this.http.post<Recipe[]>('http://localhost:5000/recipes/search', { ingredients: term }).pipe(
      tap(results => {
        this.searchResultsSource.next(results);
      })
    );
  }
// קבלת רשימת כל המתכונים הקיימים מהשרת
  getRecipes(): Observable<Recipe[]> {
    return this.http.get<Recipe[]>(this.apiUrl);
  }
// שליפת פרטים מלאים של מתכון ספציפי לפי ה-ID שלו
  getRecipeById(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${id}`);
  }
// מחיקת מתכון מהמערכת (דורש ID של המתכון)
  deleteRecipe(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
// שליחת דירוג כוכבים חדש למתכון ספציפי
  rateRecipe(recipeId: number, newRating: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${recipeId}/rate`, { rating: newRating });
  }
// פנייה לשרת לקבלת רשימת כל המשתמשים (זמין למנהל בלבד)
getAllUsers(adminEmail: string): Observable<any[]> {
  const headers = this.getAdminHeaders(adminEmail);
  // שינוי מ- http://localhost:5000/api/users לכתובת הפשוטה
  return this.http.get<any[]>('http://localhost:5000/users', { headers });
}

// שליחת בקשת אישור למשתמש (POST) - מנהל מאשר משתמש להעלות תוכן
approveUser(adminEmail: string, userId: number): Observable<any> {
  const headers = this.getAdminHeaders(adminEmail);
  return this.http.post(`http://localhost:5000/approve_user/${userId}`, {}, { headers });
}

// שליחת בקשת מחיקת משתמש לשרת (כולל ניקוי קבציו)
deleteUserFromAdmin(adminEmail: string, userId: number): Observable<any> {
  const headers = this.getAdminHeaders(adminEmail);
  return this.http.delete(`http://localhost:5000/delete_user/${userId}`, { headers });
}
// פונקציות עזר מהירות לבדיקת סטטוס המשתמש מהזיכרון המקומי
  isAdmin(): boolean { return localStorage.getItem('userRole') === 'Admin'; }
  isLoggedIn(): boolean { return !!localStorage.getItem('userEmail'); }

// שליחת בקשה מהמשתמש למנהל להפוך ל"מעלה תוכן" מאושר
requestContentRole(userId: number): Observable<any> {
    return this.http.post(`http://localhost:5000/api/request-content-role/${userId}`, {});
}

// שליפת האובייקט הנוכחי של המשתמש המחובר מה-Subject
  getCurrentUser() {
    return this.userSubject.value;
  }

// קבלת נתוני משתמש ספציפי מהשרת לפי ID
getUserById(id: number): Observable<any> {
  return this.http.get(`http://localhost:5000/api/users/${id}`);
}

// שליפת כל המתכונים שמשתמש ספציפי העלה
getUserRecipes(userId: number): Observable<any[]> {
  return this.http.get<any[]>(`http://localhost:5000/api/my-recipes/${userId}`);
}

}
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RecipeService } from '../services/recipe.service';
import { Router, RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Subject } from 'rxjs';
import { takeUntil, first, distinctUntilKeyChanged } from 'rxjs/operators';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class ProfileComponent implements OnInit, OnDestroy {
  user: any = null;
  myRecipes: any[] = [];
  private destroy$ = new Subject<void>();

  constructor(private recipeService: RecipeService, private http: HttpClient, private router: Router) {}

ngOnInit() {
  this.recipeService.user$
    .pipe(
      takeUntil(this.destroy$),
      // הקוד ימשיך הלאה רק אם ה-ID של המשתמש השתנה. 
      // זה עוצר את הלולאה שנגרמת מעדכון הנתונים בתוך loadUserData
      distinctUntilKeyChanged('id') 
    )
    .subscribe(userData => {
      if (userData && userData.id) {
        this.loadUserData(userData.id);
      }
    });
}

  private loadUserData(userId: number) {
    if (!userId) return;
    
    this.http.get(`http://127.0.0.1:5000/api/users/${userId}`)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (updatedUser: any) => {
  const newUserObj = {
    id: updatedUser.id,
    userName: updatedUser.userName || updatedUser.Name,
    email: updatedUser.email || updatedUser.Email,
    role: updatedUser.role,
    request_pending: updatedUser.request_pending || false,
    is_content_user: updatedUser.is_content_user || updatedUser.role === 'ContentCreator'
  };

  // רק אם יש הבדל אמיתי בנתונים, נעדכן את הסטטוס הגלובלי
  if (JSON.stringify(this.user) !== JSON.stringify(newUserObj)) {
      this.user = newUserObj;
      this.recipeService.updateUser(this.user);
  }
  
  this.loadMyRecipes(userId);
},
        error: (err) => {
          console.error("שגיאה בטעינה:", err);
        }
      });
  }

  loadMyRecipes(userId: number) {
    this.recipeService.getUserRecipes(userId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (recipes) => {
          this.myRecipes = recipes;
        },
        error: (err) => console.error("שגיאה בטעינת המתכונים שלי", err)
      });
  }

  sendRequest() {
    const userId = this.user?.id;
    if (userId) {
      this.recipeService.requestContentRole(userId)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            alert('הבקשה נשלחה!');
            this.loadUserData(userId);
          },
          error: (err) => console.error(err)
        });
    }
  }

  confirmDelete(recipeId: number) {
    if (confirm('האם את בטוחה שברצונך למחוק את המתכון?')) {
      this.http.delete(`http://127.0.0.1:5000/api/recipes/${recipeId}`)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.myRecipes = this.myRecipes.filter(r => r.id !== recipeId);
            alert('המתכון נמחק');
          },
          error: (err) => console.error('שגיאה במחיקה', err)
        });
    }
  }

  editRecipe(recipeId: number) {
    this.router.navigate(['/add-recipe'], { queryParams: { id: recipeId } });
  }

  ngOnDestroy() {
    // עצור את כל ה-subscriptions כשיוצאים מהדף
    this.destroy$.next();
    this.destroy$.complete();
  }
}

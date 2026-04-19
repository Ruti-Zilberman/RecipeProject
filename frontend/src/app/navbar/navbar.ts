import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RecipeService } from '../services/recipe.service';
import { FormsModule } from '@angular/forms';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class NavbarComponent implements OnInit {
  searchTerm: string = '';
  isRecipePage: boolean = false; // משתנה לזיהוי אם אנחנו בדף המתכונים
  currentUser: any = null; // יחזיק את נתוני המשתמש המחובר

  constructor(public recipeService: RecipeService, private router: Router) {
    // האזנה לשינויי נתיב: בודק בכל מעבר דף אם להציג את שורת החיפוש
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.isRecipePage = this.router.url === '/recipes';
    });
  }

  ngOnInit() {
    // הרשמה לשידור מהסרוויס: מעדכן את המשתנה המקומי בכל פעם שהמשתמש משתנה
    this.recipeService.user$.subscribe(user => {
      this.currentUser = user;
    });
  }

  // בדיקה האם למשתמש יש הרשאה להוסיף מתכון (מנהל או מעלה תוכן)
  canUploadRecipe(): boolean {
    const role = this.currentUser?.role;
    return role === 'Admin' || role === 'ContentCreator';
  }

  // ביצוע התנתקות: קורא לסרוויס לניקוי הזיכרון ומעביר לדף הבית
  logout() {
    this.recipeService.logout(); 
    this.router.navigate(['/']); 
  }

  // עדכון הסרוויס בטקסט החיפוש בכל פעם שהמשתמש מקליד
  onSearch(event: any) {
    this.recipeService.updateSearchTerm(event.target.value);
  }
}
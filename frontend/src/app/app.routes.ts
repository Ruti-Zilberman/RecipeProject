import { Routes } from '@angular/router';
import { RecipeListComponent } from './recipe-list/recipe-list';
import { LoginComponent } from './login/login';
import { RegisterComponent } from './register/register';
import { RecipeDetailsComponent } from './recipe-details/recipe-details';
import { AddRecipeComponent } from './add-recipe/add-recipe'; // הקומפוננטה שנבנה מיד
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard';
import { authGuard } from './auth.guard';
import {HomeComponent} from './home/home'
import { ProfileComponent } from './profile/profile';
export const routes: Routes = [
  { path: '', component: HomeComponent },    // ניתוב ברירת מחדל
  { path: 'recipes', component: RecipeListComponent },  // דף הבית עם כל המתכונים  
  { path: 'recipes/:id', component: RecipeDetailsComponent },  // דף פרטי מתכון (לפי ID)
  { path: 'add-recipe', component: AddRecipeComponent,canActivate: [authGuard] },// דף הוספת מתכון חדש
  { path: 'admin', component: AdminDashboardComponent },          
  { path: 'login', component: LoginComponent },                     // דף התחברות
  { path: 'register', component: RegisterComponent },               // דף הרשמה
   { path: 'profile', component: ProfileComponent }, // הנתיב החדש 
  { path: '**', redirectTo: '/recipes' }                           // הגנה מפני דפים לא קיימים
];
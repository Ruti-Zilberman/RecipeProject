import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router'; 
import { RecipeService } from '../services/recipe.service'; 
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-recipe-details',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './recipe-details.html',
  styleUrl: './recipe-details.css'
})
export class RecipeDetailsComponent implements OnInit {
  recipe: any;// משתנה שיחזיק את כל פרטי המתכון (שם, מרכיבים, הוראות וכו')

  constructor(
    private route: ActivatedRoute,// מאפשר גישה לפרמטרים בכתובת (כמו ה-ID)
    private recipeService: RecipeService // הסרוויס שפונה לשרת
  ) {}

  ngOnInit() {
    // שליפת ה-ID מה-URL והפיכתו למספר
    const id = Number(this.route.snapshot.paramMap.get('id'));

    if (id) {
      // פנייה לשרת לקבלת פרטי המתכון הספציפי
      this.recipeService.getRecipeById(id).subscribe({
        next: (data: any) => {
          this.recipe = data; 
          console.log('המתכון נטען בהצלחה:', data);
        },
        error: (err: any) => {
          console.error('שגיאה בטעינת המתכון:', err);
          this.recipe = null; 
        }
      });
    }
  }

getVariationArray(paths: any): string[] {
  if (!paths) return [];
  
  let array: string[] = [];
  
  if (Array.isArray(paths)) {
    array = paths;
  } else if (typeof paths === 'string') {
    // אם זו מחרוזת עם פסיקים, נהפוך למערך
    array = paths.split(',').map(p => p.trim()).filter(p => p !== '');
  }

  // הוספת "חותמת זמן" כדי להכריח את הדפדפן לרענן את התמונה ולא להשתמש בישנה
  return array.map(path => `${path}?t=${new Date().getTime()}`);
}
// פונקציה לעיבוד נתיבי תמונות והוספת מנגנון למניעת Cache (שמירה בזיכרון הישן)
 formatImageUrl(path: any): string {
  if (!path) return '';
  
  // אם הנתיב כבר כולל סימן שאלה (כלומר כבר הוספנו זמן), לא נוסיף שוב
  const separator = path.includes('?') ? '&' : '?';
  const timeStamp = `t=${new Date().getTime()}`;// יוצר קוד ייחודי לפי זמן

  let pathStr = String(path).trim().replace(/^\/+/, '').replace('static/', '');

  if (pathStr.startsWith('http')) {
    return pathStr.includes('?') ? pathStr : `${pathStr}${separator}${timeStamp}`;
  }

  if (!pathStr.includes('uploads/')) {
    pathStr = 'uploads/' + pathStr;
  }

  // מחזירים את הכתובת עם חותמת זמן כדי למנוע טעינה מהזיכרון הישן
  return `http://localhost:5000/${pathStr}${separator}${timeStamp}`;
}
// טיפול בשגיאה בטעינת תמונה - החלפה לתמונת ברירת מחדל
  handleImageError(img: HTMLImageElement) {
    console.warn("Image failed to load:", img.src);
    // ננסה להוסיף static/ לפני הנתיב אם הוא נכשל
    if (!img.src.includes('/static/')) {
        const parts = img.src.split('localhost:5000/');
        if (parts.length > 1) {
            img.src = `http://localhost:5000/static/${parts[1]}`;
            img.onerror = () => { 
                img.src = 'assets/default-recipe.jpg'; 
                img.onerror = null; 
            };
            return;
        }
    }
    img.src = 'assets/default-recipe.jpg';
    img.onerror = null; 
  }
}
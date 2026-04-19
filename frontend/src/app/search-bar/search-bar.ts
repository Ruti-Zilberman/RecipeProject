import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common'; 

@Component({
  selector: 'app-search-bar',
  standalone: true,    
  imports: [CommonModule], 
  templateUrl: './search-bar.html',
  styleUrls: ['./search-bar.css']
})
export class SearchBarComponent {
  // --- EventEmitter ו-Output ---
  // @Output מאפשר לקומפוננטה הזו "לדבר" עם הקומפוננטה שמכילה אותה (האבא).
  // searchChanged הוא הצינור שדרכו נשלח את המידע החוצה.
  @Output() searchChanged = new EventEmitter<string>();

  // פונקציה שמופעלת בכל פעם שהמשתמש מקליד משהו בתיבת החיפוש
  onSearch(event: any) {
    // שליפת הערך מתוך האירוע (מה שהמשתמש כתב ב-Input)
    const value = event.target.value;
    
    // שליחת הערך החוצה. כל מי שמקשיב ל-(searchChanged) יקבל את הטקסט המעודכן.
    this.searchChanged.emit(value);
  }
}
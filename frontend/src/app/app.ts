import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './navbar/navbar';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet,NavbarComponent], // השאירי רק את RouterOutlet
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  // הקלאס נשאר כמעט ריק - הוא רק מציג את ה-HTML הראשי
}
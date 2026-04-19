import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app'; // שינינו מ-App ל-AppComponent

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router'; // חייב לייבא את זה
import { routes } from './app.routes'; // ודאי שהנתיב לקובץ הראוטים נכון
import { provideHttpClient } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes), // השורה הזו היא ה"מנוע" של המעבר בין דפים
    provideHttpClient()
  ]
};
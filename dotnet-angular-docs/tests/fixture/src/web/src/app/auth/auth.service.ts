import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly loggedIn = signal(false);

  isLoggedIn(): boolean {
    return this.loggedIn();
  }

  hasRole(role: string): boolean {
    return role === 'User';
  }
}

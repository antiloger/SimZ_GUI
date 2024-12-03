// src/auth.ts
import { invoke } from '@tauri-apps/api/core';

interface LoginCredentials {
  username: string;
  password: string;
}

export class AuthService {
  private static TOKEN_KEY = 'auth_token';

  static async login(credentials: LoginCredentials): Promise<boolean> {
    try {
      const token = await invoke<string>('login', { credentials });
      localStorage.setItem(this.TOKEN_KEY, token);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  }

  static async verifyToken(token: string): Promise<boolean> {
    try {
      await invoke('verify_token', { token });
      return true;
    } catch {
      return false;
    }
  }

  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  static logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
  }

  static async isAuthenticated(): Promise<boolean> {
    const token = this.getToken();
    if (!token) return false;
    return this.verifyToken(token);
  }

  static async callProtectedRoute(): Promise<string> {
    const token = this.getToken();
    if (!token) throw new Error('No token found');

    return invoke('protected_route', { token });
  }
}

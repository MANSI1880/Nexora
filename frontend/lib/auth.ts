import { apiClient } from './api';
import { Token, UserResponse } from '../types/api';

export const authApi = {
  login: async (username: string, password: string):Promise<Token> => {
    // FastAPI OAuth2PasswordRequestForm expects form-urlencoded data
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post<Token>('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (username: string, email: string, password: string):Promise<UserResponse> => {
    const response = await apiClient.post<UserResponse>('/api/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination
      window.location.href = '/login';
    }
  },
};

export function getUserRole(): string {
  if (typeof window === 'undefined') return 'user';

  const token = localStorage.getItem('token');
  if (!token) return 'user';

  try {
    const parts = token.split('.');
    if (parts.length !== 3) return 'user';

    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    const payload = JSON.parse(jsonPayload);
    if (typeof payload?.role === 'string') {
      const normalizedRole = payload.role.trim().toLowerCase();
      if (['admin', 'it_support', 'user'].includes(normalizedRole)) {
        return normalizedRole;
      }
    }
  } catch {
    return 'user';
  }
  return 'user';
}

export function canApproveTickets(): boolean {
  const role = getUserRole();
  return role === 'admin' || role === 'it_support';
}

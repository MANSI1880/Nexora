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
      window.location.href = '/login';
    }
  },
};

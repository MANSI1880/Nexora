import { apiClient } from './api';
import { TicketResponse, TicketCreate, TicketUpdate } from '../types/api';

export const ticketsApi = {
  getAll: async (): Promise<TicketResponse[]> => {
    const response = await apiClient.get<TicketResponse[]>('/api/tickets');
    return response.data;
  },

  getById: async (id: string | number): Promise<TicketResponse> => {
    const response = await apiClient.get<TicketResponse>(`/api/tickets/${id}`);
    return response.data;
  },

  create: async (data: TicketCreate): Promise<TicketResponse> => {
    const response = await apiClient.post<TicketResponse>('/api/tickets', data);
    return response.data;
  },

  update: async (id: string | number, data: TicketUpdate): Promise<TicketResponse> => {
    const response = await apiClient.put<TicketResponse>(`/api/tickets/${id}`, data);
    return response.data;
  }
};

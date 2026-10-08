import { apiClient } from './api';
import { ChatRequest, ChatResponse } from '../types/api';

export const chatApi = {
  sendMessage: async (message: string, conversation_id?: string): Promise<ChatResponse> => {
    const payload: ChatRequest = { message };
    if (conversation_id) {
      payload.conversation_id = conversation_id;
    }
    const response = await apiClient.post<ChatResponse>('/api/chat', payload);
    return response.data;
  },
};

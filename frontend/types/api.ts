export interface UserResponse {
  id: number;
  username: string;
  email: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  intent: string;
  confidence: number;
  sources: string[];
  ticket_id?: string;
  action?: string;
  status: string;
}

export interface TicketCreate {
  title: string;
  description: string;
  priority?: string;
}

export interface TicketUpdate {
  status?: string;
  priority?: string;
}

export interface TicketResponse {
  id: number;
  title: string;
  description: string;
  priority: string;
  status: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

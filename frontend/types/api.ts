export interface UserResponse {
  id: string | number;
  username: string;
  email: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface ChatResponse {
  response: string;
  intent: string;
  confidence: number;
  sources: string[];
  ticket_id?: string;
  action: string;
  status: string;
}

export interface TicketResponse {
  id: string | number;
  title?: string;
  description?: string;
  status: string;
  created_at: string;
}

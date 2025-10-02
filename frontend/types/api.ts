export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

export interface SyncStatus {
  gmail: {
    connected: boolean;
    last_sync: string | null;
  };
  hubspot: {
    connected: boolean;
    last_sync: string | null;
  };
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export interface SyncResponse {
  synced: number;
  status: string;
}

import axios from 'axios';

// API URL - defaults to localhost for development
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 second timeout
});

export const api = {
  auth: {
    getConnectToken: () => apiClient.post('/api/v1/auth/connect-token'),
  },
  integrations: {
    saveGmailAccount: (account_id: string) =>
      apiClient.post('/api/v1/integrations/gmail/save', { account_id }),
    saveHubSpotAccount: (account_id: string) =>
      apiClient.post('/api/v1/integrations/hubspot/save', { account_id }),
  },
  sync: {
    syncGmail: () => apiClient.post('/api/v1/sync/gmail'),
    syncHubSpot: () => apiClient.post('/api/v1/sync/hubspot'),
    getStatus: () => apiClient.get('/api/v1/sync/status'),
  },
  agent: {
    chat: (message: string) =>
      apiClient.post('/api/v1/agent/chat', { message }),
  },
};

export default apiClient;

import api from './axios';

export const chatAPI = {
  // Get all conversations for the current user
  getConversations: () => api.get('/api/chat/conversations'),

  // Create a new conversation
  createConversation: (data = {}) => api.post('/api/chat/conversations', data),

  // Get a specific conversation with messages
  getConversation: (conversationId) => api.get(`/api/chat/conversations/${conversationId}`),

  // Send a message to a conversation
  sendMessage: (conversationId, content) => 
    api.post(`/api/chat/conversations/${conversationId}/messages`, { content }),
};

import apiClient from './client';

/**
 * Idea and Market Analysis API Service Client
 * Handles communication with backend validation, health, and search routes.
 */

export const ideaApi = {
  /**
   * Health Check: Verify backend reachability
   */
  checkHealth: async () => {
    return apiClient.get('/health/');
  },

  /**
   * Submit Idea for Multi-Agent Validation
   * @param {Object} ideaData - Startup idea payload
   */
  validateIdea: async (ideaData) => {
    return apiClient.post('/idea/validate', ideaData);
  },

  /**
   * Retrieve Historical Validation Report by ID
   * @param {string} ideaId - Unique report ID
   */
  getValidationReport: async (ideaId) => {
    return apiClient.get(`/idea/${ideaId}`);
  },

  /**
   * Execute Direct Market Search via Tavily
   * @param {string} query - Search term
   * @param {number} maxResults - Max items
   */
  searchMarket: async (query, maxResults = 5) => {
    return apiClient.post('/search/market', { query, max_results: maxResults });
  },
};

export default ideaApi;

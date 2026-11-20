import { useState, useCallback } from 'react';
import ideaApi from '@/api/ideaApi';

/**
 * Custom Hook: useIdeaValidation
 * Encapsulates the execution state and errors when validating ideas.
 */
export const useIdeaValidation = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const validate = useCallback(async (ideaPayload) => {
    setLoading(true);
    setError(null);
    try {
      const response = await ideaApi.validateIdea(ideaPayload);
      setData(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || 'Validation request failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, validate };
};

export default useIdeaValidation;

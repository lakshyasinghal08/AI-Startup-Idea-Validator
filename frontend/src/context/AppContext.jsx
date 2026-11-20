import React, { createContext, useContext, useState } from 'react';

/**
 * Global App Context
 * Manages shared state such as recent idea validations and user preferences.
 * Placeholder for Milestone 1. Extended in Milestone 5 for user authentication.
 */

const AppContext = createContext(null);

export const AppProvider = ({ children }) => {
  const [recentIdeas, setRecentIdeas] = useState([]);
  const [activeIdea, setActiveIdea] = useState(null);

  const addRecentIdea = (idea) => {
    setRecentIdeas((prev) => [idea, ...prev]);
  };

  return (
    <AppContext.Provider value={{ recentIdeas, activeIdea, setActiveIdea, addRecentIdea }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;

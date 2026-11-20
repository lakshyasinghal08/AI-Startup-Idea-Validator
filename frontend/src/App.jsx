import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from '@/layouts/MainLayout';
import HomePage from '@/pages/HomePage';
import ValidatorPage from '@/pages/ValidatorPage';
import AboutPage from '@/pages/AboutPage';
import NotFoundPage from '@/pages/NotFoundPage';

/**
 * Root Application Component
 * Defines declarative route tree using React Router DOM.
 * Only includes Home, Validator, About, and 404 pages for Milestone 1.
 */
export const App = () => {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="validator" element={<ValidatorPage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

export default App;

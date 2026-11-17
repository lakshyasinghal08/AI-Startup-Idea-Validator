import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Home } from 'lucide-react';
import Button from '@/components/common/Button';

export const NotFoundPage = () => {
  return (
    <div className="text-center py-20 space-y-6 max-w-md mx-auto">
      <div className="w-16 h-16 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center mx-auto">
        <AlertCircle className="w-8 h-8" />
      </div>
      <div>
        <h1 className="text-4xl font-extrabold text-slate-900">404</h1>
        <p className="text-slate-600 mt-2">The page you are looking for does not exist.</p>
      </div>
      <Link to="/">
        <Button variant="primary" className="space-x-2">
          <Home className="w-4 h-4" />
          <span>Return Home</span>
        </Button>
      </Link>
    </div>
  );
};

export default NotFoundPage;

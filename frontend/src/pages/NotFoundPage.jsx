import React from 'react';
import { Link } from 'react-router-dom';
import Button from '@/components/common/Button';

export const NotFoundPage = () => {
  return (
    <div className="text-center py-20 space-y-4 max-w-md mx-auto">
      <div className="text-5xl font-bold text-slate-800">404</div>
      <div className="space-y-1">
        <h1 className="text-lg font-semibold text-slate-900">Page Not Found</h1>
        <p className="text-sm text-slate-500">
          The requested URL does not exist or has been removed.
        </p>
      </div>
      <div className="pt-2">
        <Link to="/">
          <Button variant="primary">Return Home</Button>
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;

import React from 'react';

export const Button = ({
  children,
  type = 'button',
  variant = 'primary',
  disabled = false,
  className = '',
  onClick,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-medium rounded-lg text-sm px-4 py-2.5 transition focus:outline-none focus:ring-2 focus:ring-offset-1';

  const variants = {
    primary:
      'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500 disabled:bg-blue-300',
    secondary:
      'bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 focus:ring-slate-400 disabled:bg-slate-100 disabled:text-slate-400',
    outline:
      'bg-transparent hover:bg-slate-100 text-slate-700 border border-slate-300 focus:ring-slate-400',
  };

  const disabledStyles = disabled
    ? 'opacity-60 cursor-not-allowed pointer-events-none'
    : '';

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant] || variants.primary} ${disabledStyles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;

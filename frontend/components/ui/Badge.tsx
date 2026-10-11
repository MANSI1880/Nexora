import React from 'react';

export type BadgeColor = 'gray' | 'blue' | 'green' | 'red' | 'yellow' | 'purple' | 'emerald' | 'rose';

export function Badge({
  children,
  color = 'gray',
  className = '',
}: {
  children: React.ReactNode;
  color?: BadgeColor;
  className?: string;
}) {
  const colors: Record<BadgeColor, string> = {
    gray: 'bg-gray-100 text-gray-800 border-gray-200',
    blue: 'bg-blue-100 text-blue-800 border-blue-200',
    green: 'bg-green-100 text-green-800 border-green-200',
    red: 'bg-red-100 text-red-800 border-red-200',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    purple: 'bg-purple-100 text-purple-800 border-purple-200',
    emerald: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    rose: 'bg-rose-100 text-rose-800 border-rose-200',
  };

  return (
    <span
      role="status"
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colors[color]} ${className}`}
    >
      {children}
    </span>
  );
}

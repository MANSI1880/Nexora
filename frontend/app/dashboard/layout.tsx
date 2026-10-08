'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authApi } from '@/lib/auth';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    authApi.logout();
  };

  const navItems = [
    { name: 'Welcome', href: '/dashboard' },
    { name: 'AI IT Support', href: '/dashboard/chat' },
    { name: 'My Tickets', href: '/dashboard/tickets' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      <aside className="w-full md:w-64 bg-slate-900 text-white flex flex-col shrink-0">
        <div className="p-6">
          <h1 className="text-2xl font-bold">Nexora</h1>
          <p className="text-sm text-slate-400 mt-1">IT Service Desk</p>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link 
                key={item.name}
                href={item.href} 
                className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-blue-600' : 'hover:bg-slate-800'
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center px-4 py-3 hover:bg-slate-800 rounded-lg cursor-pointer text-sm font-medium transition-colors">
            <span>User Account</span>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full text-left flex items-center px-4 py-3 hover:bg-slate-800 rounded-lg text-sm font-medium text-red-400 transition-colors mt-1"
          >
            Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="bg-white shadow-sm border-b border-gray-200 shrink-0">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <h1 className="text-xl font-semibold text-gray-900 capitalize">
              {pathname.split('/').pop() === 'dashboard' ? 'Dashboard' : pathname.split('/').pop()?.replace('-', ' ')}
            </h1>
          </div>
        </header>

        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </main>
    </div>
  );
}

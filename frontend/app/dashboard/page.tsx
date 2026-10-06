'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/auth';
import Link from 'next/link';

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    authApi.logout();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold">Nexora</h1>
          <p className="text-sm text-slate-400 mt-1">IT Service Desk</p>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-2">
          <Link href="/dashboard" className="flex items-center px-4 py-3 bg-slate-800 rounded-lg text-sm font-medium transition-colors">
            Welcome
          </Link>
          <Link href="/dashboard/chat" className="flex items-center px-4 py-3 hover:bg-slate-800 rounded-lg text-sm font-medium transition-colors">
            AI IT Support
          </Link>
          <Link href="/dashboard/tickets" className="flex items-center px-4 py-3 hover:bg-slate-800 rounded-lg text-sm font-medium transition-colors">
            My Tickets
          </Link>
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

      {/* Main content */}
      <main className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
          </div>
        </header>

        <div className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          <div className="bg-white shadow-sm border border-gray-200 rounded-lg p-6 h-full">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to Nexora IT Service Desk</h2>
            <p className="text-gray-600 mb-8 max-w-2xl">
              Describe your IT problems conversationally to get AI-driven classification, 
              troubleshooting, and automated actions through controlled tools.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI IT Support</h3>
                <p className="text-gray-600 mb-4 text-sm">
                  Interact with our LangGraph-powered AI agent to troubleshoot VPN, software, and hardware issues.
                </p>
                <Link href="/dashboard/chat" className="text-blue-600 font-medium text-sm hover:underline">
                  Start Chat &rarr;
                </Link>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">My Tickets</h3>
                <p className="text-gray-600 mb-4 text-sm">
                  View, manage, and track the status of your IT support tickets.
                </p>
                <Link href="/dashboard/tickets" className="text-blue-600 font-medium text-sm hover:underline">
                  View Tickets &rarr;
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

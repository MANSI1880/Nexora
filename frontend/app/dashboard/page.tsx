'use client';

import Link from 'next/link';

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="bg-white overflow-hidden shadow rounded-lg mb-8 border border-gray-200">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Nexora</h2>
          <p className="text-gray-600 max-w-3xl">
            This is your autonomous IT Service Desk. Nexora uses an advanced multi-agent AI system 
            to automatically diagnose, resolve, and route IT requests using our enterprise knowledge base.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link href="/dashboard/chat" className="group block">
          <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 h-full hover:border-blue-500 hover:ring-1 hover:ring-blue-500 transition-all">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                  <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="ml-3 text-lg font-medium text-gray-900">Start Chat</h3>
              </div>
              <p className="text-sm text-gray-500 group-hover:text-gray-900">
                Talk to the Nexora AI to resolve your IT issues immediately.
              </p>
            </div>
          </div>
        </Link>

        <Link href="/dashboard/tickets" className="group block">
          <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 h-full hover:border-blue-500 hover:ring-1 hover:ring-blue-500 transition-all">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="ml-3 text-lg font-medium text-gray-900">View Tickets</h3>
              </div>
              <p className="text-sm text-gray-500 group-hover:text-gray-900">
                Check the status of your active IT requests and history.
              </p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}

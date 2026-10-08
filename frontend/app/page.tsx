import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl text-center space-y-8">
        <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight sm:text-6xl">
          Nexora <span className="text-blue-600">IT Service Desk</span>
        </h1>
        <p className="mt-4 text-xl text-gray-600 max-w-2xl mx-auto">
          Autonomous multi-agent AI platform. Describe your problems conversationally, 
          get instant classification, troubleshooting, and automated resolutions.
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <Link 
            href="/login" 
            className="rounded-md bg-blue-600 px-8 py-3 text-base font-medium text-white hover:bg-blue-700 shadow-sm transition-colors"
          >
            Sign in
          </Link>
          <Link 
            href="/register" 
            className="rounded-md bg-white border border-gray-300 px-8 py-3 text-base font-medium text-gray-700 hover:bg-gray-50 shadow-sm transition-colors"
          >
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}

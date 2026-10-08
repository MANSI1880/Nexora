import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Nexora IT Service Desk',
  description: 'Autonomous multi-agent AI IT Service Desk platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">{children}</body>
    </html>
  );
}

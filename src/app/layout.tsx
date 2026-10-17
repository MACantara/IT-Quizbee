import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'IT Quizbee - Interactive IT Reviewer',
    template: 'IT Quizbee - %s',
  },
  description: 'Master Your IT Knowledge',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 min-h-screen flex flex-col">
        {/* hoisted to <head> by React 19 */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css"
        />
        <header className="bg-white shadow-md">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition">
                <i className="bi bi-trophy-fill text-4xl text-yellow-500" />
                <div>
                  <h1 className="text-3xl font-bold text-gray-800">IT Quizbee</h1>
                  <p className="text-sm text-gray-600">Master Your IT Knowledge</p>
                </div>
              </Link>
            </div>
          </div>
        </header>
        {children}
        <footer className="bg-white shadow-md">
          <div className="container mx-auto px-4 py-6 text-center text-gray-600">
            <p>&copy; 2025 IT Quizbee. Built with Next.js, Tailwind CSS, and Bootstrap Icons.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}

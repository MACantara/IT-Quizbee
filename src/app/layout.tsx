import type { Metadata } from 'next';
import Link from 'next/link';
import { Public_Sans, Roboto_Mono } from 'next/font/google';
import { Trophy } from 'lucide-react';
import './globals.css';

const publicSans = Public_Sans({
  subsets: ['latin'],
  variable: '--font-public-sans',
});

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  variable: '--font-roboto-mono',
});

export const metadata: Metadata = {
  title: {
    default: 'IT Quizbee - Interactive IT Reviewer',
    template: 'IT Quizbee - %s',
  },
  description: 'Master Your IT Knowledge',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${publicSans.variable} ${robotoMono.variable}`}>
      <body className="flex min-h-screen flex-col font-sans">
        <header className="border-b-2 border-ink bg-white">
          <div className="container mx-auto flex items-center justify-between px-4 py-4">
            <Link href="/" className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center border-2 border-ink">
                <Trophy className="h-5 w-5 text-ink" strokeWidth={2.25} aria-hidden />
              </span>
              <span>
                <span className="block text-xl font-bold tracking-tight text-ink">
                  IT Quizbee
                </span>
                <span className="num block text-xs text-ink-soft">
                  Answer sheet · Solo practice
                </span>
              </span>
            </Link>
            <span className="num hidden border border-line px-2 py-1 text-xs text-ink-soft sm:inline-block">
              FORM Q-1
            </span>
          </div>
        </header>
        {children}
        <footer className="border-t-2 border-ink bg-white">
          <div className="container mx-auto px-4 py-5 text-center">
            <p className="text-sm text-ink-soft">
              &copy; 2025 IT Quizbee. Built with Next.js, Tailwind CSS, and Lucide.
            </p>
            <p className="num mt-1 text-xs text-ink-soft">
              Scores and progress stay on this device.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}

import Link from 'next/link';
import { CircleHelp, House } from 'lucide-react';

export default function NotFound() {
  return (
    <main className="container mx-auto flex flex-grow items-center justify-center px-4 py-8">
      <div className="sheet w-full max-w-md p-8 text-center">
        <CircleHelp className="mx-auto mb-4 h-10 w-10 text-ink-soft" aria-hidden />
        <h2 className="num mb-2 text-5xl font-bold text-ink">404</h2>
        <p className="mb-6 text-ink-soft">The page you&apos;re looking for doesn&apos;t exist.</p>
        <Link href="/" className="btn btn-pencil">
          <House className="h-4 w-4" aria-hidden />
          Home
        </Link>
      </div>
    </main>
  );
}

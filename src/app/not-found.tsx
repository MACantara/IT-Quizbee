import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="container mx-auto px-4 py-8 flex-grow flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <i className="bi bi-question-circle text-6xl text-gray-400 mb-4" />
        <h2 className="text-3xl font-bold text-gray-800 mb-2">404</h2>
        <p className="text-gray-600 mb-6">The page you&apos;re looking for doesn&apos;t exist.</p>
        <Link
          href="/"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition inline-block"
        >
          <i className="bi bi-house mr-2" />Home
        </Link>
      </div>
    </main>
  );
}

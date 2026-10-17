'use client';

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="container mx-auto px-4 py-8 flex-grow flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <i className="bi bi-exclamation-triangle text-6xl text-yellow-500 mb-4" />
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Something went wrong</h2>
        <p className="text-gray-600 mb-6">An unexpected error occurred.</p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <i className="bi bi-arrow-repeat mr-2" />Try Again
        </button>
      </div>
    </main>
  );
}

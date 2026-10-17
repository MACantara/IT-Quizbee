import Link from 'next/link';

const FEATURES = [
  { icon: 'bi-check-circle-fill text-blue-600', bg: 'bg-blue-50', title: '10 Topics', sub: 'Comprehensive coverage' },
  { icon: 'bi-clock-fill text-green-600', bg: 'bg-green-50', title: 'Multiple Modes', sub: 'Practice your way' },
  { icon: 'bi-trophy-fill text-purple-600', bg: 'bg-purple-50', title: 'Three Game Modes', sub: 'Elimination, Finals & Review' },
  { icon: 'bi-lightbulb-fill text-pink-600', bg: 'bg-pink-50', title: 'Explanations', sub: 'Learn from answers' },
];

const MODES = [
  {
    href: '/quiz/elimination',
    border: 'border-blue-500',
    bg: 'from-blue-50 to-blue-100',
    icon: 'bi-lightning-charge-fill text-blue-600',
    check: 'text-blue-600',
    btn: 'bg-blue-600',
    title: 'Elimination',
    items: ['100 random questions', 'From all 10 topics', '60 minutes total'],
    cta: 'Start Elimination',
  },
  {
    href: '/quiz/finals',
    border: 'border-purple-500',
    bg: 'from-purple-50 to-purple-100',
    icon: 'bi-trophy-fill text-purple-600',
    check: 'text-purple-600',
    btn: 'bg-purple-600',
    title: 'Finals',
    items: ['30 identification questions', 'Easy, Average, Difficult', 'Timed questions'],
    cta: 'Start Finals',
  },
  {
    href: '/topics',
    border: 'border-green-500',
    bg: 'from-green-50 to-green-100',
    icon: 'bi-book-fill text-green-600',
    check: 'text-green-600',
    btn: 'bg-green-600',
    title: 'Review',
    items: ['Choose any topic', 'Select subtopics', 'Practice at your pace'],
    cta: 'Start Review',
  },
];

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8 flex-grow">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 animate-fade-in">
          <div className="text-center mb-8">
            <i className="bi bi-mortarboard-fill text-6xl text-purple-600 mb-4" />
            <h2 className="text-4xl font-bold text-gray-800 mb-4">Welcome to IT Quizbee!</h2>
            <p className="text-lg text-gray-600">Test your knowledge across 10 essential IT topics</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {FEATURES.map((f) => (
              <div key={f.title} className={`flex items-center gap-3 p-4 ${f.bg} rounded-lg`}>
                <i className={`bi ${f.icon} text-3xl`} />
                <div>
                  <h3 className="font-semibold text-gray-800">{f.title}</h3>
                  <p className="text-sm text-gray-600">{f.sub}</p>
                </div>
              </div>
            ))}
          </div>

          <h3 className="text-2xl font-bold text-gray-800 mb-4 text-center">Choose Your Mode</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {MODES.map((m) => (
              <Link
                key={m.title}
                href={m.href}
                className={`border-4 ${m.border} rounded-xl p-6 cursor-pointer hover:shadow-xl transition transform hover:scale-105 bg-gradient-to-br ${m.bg} block`}
              >
                <div className="text-center mb-4">
                  <i className={`bi ${m.icon} text-6xl mb-3`} />
                  <h3 className="text-2xl font-bold text-gray-800">{m.title}</h3>
                </div>
                <ul className="space-y-2 text-gray-700 mb-4 text-sm">
                  {m.items.map((item) => (
                    <li key={item} className="flex items-center gap-2">
                      <i className={`bi bi-check-circle-fill ${m.check}`} />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
                <div className={`w-full py-3 ${m.btn} text-white rounded-lg font-semibold text-center`}>
                  {m.cta}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}

'use client';

import { useState } from 'react';
import { Modal } from './Modal';
import { getUserName, setUserName } from '@/lib/attempts';

const COLORS = {
  blue: { icon: 'text-blue-600', bg: 'bg-blue-100', btn: 'bg-blue-600 hover:bg-blue-700', focus: 'focus:border-blue-500' },
  purple: { icon: 'text-purple-600', bg: 'bg-purple-100', btn: 'bg-purple-600 hover:bg-purple-700', focus: 'focus:border-purple-500' },
} as const;

export function NameModal({
  title,
  description,
  accent = 'blue',
  skip = false,
  onSubmit,
}: {
  title: string;
  description: string;
  accent?: keyof typeof COLORS;
  skip?: boolean;
  onSubmit: (name: string) => void;
}) {
  const c = COLORS[accent];
  const [name, setName] = useState(() => getUserName());
  const [open, setOpen] = useState(true);

  if (skip) return null;

  return (
    <Modal title={title} open={open}>
      <p className="text-gray-600 mb-6 text-center">{description}</p>
      <div className={`w-16 h-16 ${c.bg} rounded-full flex items-center justify-center mx-auto mb-4`}>
        <i className={`bi bi-person-fill text-3xl ${c.icon}`} />
      </div>
      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          const trimmed = name.trim();
          if (!trimmed) return;
          setUserName(trimmed);
          setOpen(false);
          onSubmit(trimmed);
        }}
      >
        <div>
          <label htmlFor="userName" className="block text-sm font-semibold text-gray-700 mb-2">
            Your Name
          </label>
          <input
            id="userName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={`w-full px-4 py-3 border-2 border-gray-300 rounded-lg ${c.focus} focus:outline-none`}
            placeholder="Enter your name"
            required
            autoFocus
          />
        </div>
        <button
          type="submit"
          className={`w-full px-6 py-3 ${c.btn} text-white rounded-lg transition font-semibold`}
        >
          <i className="bi bi-arrow-right-circle-fill mr-2" />Start Quiz
        </button>
      </form>
    </Modal>
  );
}

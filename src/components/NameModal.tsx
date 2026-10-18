'use client';

import { useState } from 'react';
import { CircleArrowRight, User } from 'lucide-react';
import { Modal } from './Modal';
import { getUserName, setUserName } from '@/lib/attempts';

export function NameModal({
  title,
  description,
  skip = false,
  onSubmit,
}: {
  title: string;
  description: string;
  skip?: boolean;
  onSubmit: (name: string) => void;
}) {
  const [name, setName] = useState(() => getUserName());
  const [open, setOpen] = useState(true);

  if (skip) return null;

  return (
    <Modal title={title} open={open}>
      <p className="mb-6 text-ink-soft">{description}</p>
      <div className="mx-auto mb-6 flex h-12 w-12 items-center justify-center border-2 border-ink">
        <User className="h-6 w-6 text-ink" aria-hidden />
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
          <label htmlFor="userName" className="field-label">
            Contestant Name
          </label>
          <input
            id="userName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="field"
            placeholder="Enter your name"
            required
            autoFocus
          />
        </div>
        <button type="submit" className="btn btn-pencil w-full">
          <CircleArrowRight className="h-4 w-4" aria-hidden />
          Start Quiz
        </button>
      </form>
    </Modal>
  );
}

'use client';

import { useEffect, useState } from 'react';

export function Modal({
  title,
  children,
  open,
  onClose,
}: {
  title: string;
  children: React.ReactNode;
  open: boolean;
  onClose?: () => void;
}) {
  useEffect(() => {
    if (!open || !onClose) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="mx-4 w-full max-w-md border-2 border-ink bg-white p-6 animate-fade-in sm:p-8"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="mb-4 border-b border-line pb-3 text-xl font-bold text-ink">{title}</h2>
        {children}
      </div>
    </div>
  );
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <Modal title={title} open={open} onClose={onCancel}>
      <p className="mb-6 text-ink-soft">{message}</p>
      <div className="flex gap-3">
        <button onClick={onCancel} className="btn btn-line flex-1">
          {cancelText}
        </button>
        <button onClick={onConfirm} className="btn btn-pencil flex-1">
          {confirmText}
        </button>
      </div>
    </Modal>
  );
}

export function useDialog() {
  const [dialog, setDialog] = useState<
    | { kind: 'confirm'; title: string; message: string; resolve: (v: boolean) => void }
    | { kind: 'warning'; title: string; message: string; resolve: () => void }
    | null
  >(null);

  const confirm = (message: string, title = 'Confirm') =>
    new Promise<boolean>((resolve) => setDialog({ kind: 'confirm', title, message, resolve }));

  const warning = (message: string, title = 'Warning') =>
    new Promise<void>((resolve) => setDialog({ kind: 'warning', title, message, resolve }));

  const element = dialog && (
    <Modal
      title={dialog.title}
      open
      onClose={dialog.kind === 'confirm' ? () => { setDialog(null); dialog.resolve(false); } : undefined}
    >
      <p className="mb-6 text-ink-soft">{dialog.message}</p>
      {dialog.kind === 'confirm' ? (
        <div className="flex gap-3">
          <button
            onClick={() => { setDialog(null); dialog.resolve(false); }}
            className="btn btn-line flex-1"
          >
            Keep Working
          </button>
          <button
            onClick={() => { setDialog(null); dialog.resolve(true); }}
            className="btn btn-pencil flex-1"
          >
            Submit Anyway
          </button>
        </div>
      ) : (
        <button
          onClick={() => { setDialog(null); dialog.resolve(); }}
          className="btn btn-pencil w-full"
        >
          OK
        </button>
      )}
    </Modal>
  );

  return { confirm, warning, dialogElement: element };
}

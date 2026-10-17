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
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">{title}</h2>
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
      <p className="text-gray-600 mb-6 text-center">{message}</p>
      <div className="flex gap-3">
        <button
          onClick={onCancel}
          className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition font-semibold"
        >
          {cancelText}
        </button>
        <button
          onClick={onConfirm}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
        >
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
      <p className="text-gray-600 mb-6 text-center">{dialog.message}</p>
      {dialog.kind === 'confirm' ? (
        <div className="flex gap-3">
          <button
            onClick={() => { setDialog(null); dialog.resolve(false); }}
            className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition font-semibold"
          >
            Keep Working
          </button>
          <button
            onClick={() => { setDialog(null); dialog.resolve(true); }}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            Submit Anyway
          </button>
        </div>
      ) : (
        <button
          onClick={() => { setDialog(null); dialog.resolve(); }}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          OK
        </button>
      )}
    </Modal>
  );

  return { confirm, warning, dialogElement: element };
}

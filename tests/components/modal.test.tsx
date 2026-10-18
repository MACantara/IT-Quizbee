import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Modal, ConfirmDialog } from '@/components/Modal';

describe('Modal', () => {
  it('renders nothing when closed', () => {
    const { container } = render(<Modal title="T" open={false}>body</Modal>);
    expect(container).toBeEmptyDOMElement();
  });

  it('renders dialog with title and children when open', () => {
    render(<Modal title="My Title" open>inner content</Modal>);
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAccessibleName('My Title');
    expect(screen.getByText('inner content')).toBeInTheDocument();
  });

  it('calls onClose on Escape and backdrop click', () => {
    const onClose = vi.fn();
    render(<Modal title="T" open onClose={onClose}>x</Modal>);
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});

describe('ConfirmDialog', () => {
  it('fires confirm and cancel callbacks', () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(
      <ConfirmDialog open title="Sure?" message="Do it?" onConfirm={onConfirm} onCancel={onCancel} />
    );
    fireEvent.click(screen.getByText('Confirm'));
    expect(onConfirm).toHaveBeenCalled();
    fireEvent.click(screen.getByText('Cancel'));
    expect(onCancel).toHaveBeenCalled();
  });
});

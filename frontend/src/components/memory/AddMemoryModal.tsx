import React, { useState } from 'react';
import { X, Brain, Tag } from 'lucide-react';
import { CreateMemoryPayload } from '../../types';

interface AddMemoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddMemory: (payload: CreateMemoryPayload) => Promise<void>;
}

export const AddMemoryModal: React.FC<AddMemoryModalProps> = ({
  isOpen,
  onClose,
  onAddMemory,
}) => {
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('architecture');
  const [importance, setImportance] = useState(3);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      setError('Memory content is required');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onAddMemory({
        content: content.trim(),
        category,
        importance,
      });
      setContent('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save memory');
    } finally {
      setIsSubmitting(false);
    }
  };

  const categories = [
    { value: 'architecture', label: 'Architecture Decision' },
    { value: 'conventions', label: 'Coding Convention' },
    { value: 'decisions', label: 'Product Decision' },
    { value: 'bugs', label: 'Bug Solution' },
    { value: 'general', label: 'General Knowledge' },
  ];

  return (
    <div className="modal-backdrop">
      <div className="modal-dialog">
        <div className="modal-header">
          <div className="modal-title">
            <Brain size={18} className="modal-icon memory" />
            <span>Add Project Memory</span>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="modal-alert-error">{error}</div>}

            <div className="form-group">
              <label className="form-label">Category</label>
              <select
                className="form-select"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                {categories.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Memory Content *</label>
              <textarea
                className="form-textarea"
                placeholder="e.g. Always use JWT stored in HttpOnly cookies for auth..."
                rows={4}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                autoFocus
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Importance Level (1-5): {importance}</label>
              <input
                type="range"
                min="1"
                max="5"
                className="form-range"
                value={importance}
                onChange={(e) => setImportance(parseInt(e.target.value, 10))}
              />
              <div className="range-labels">
                <span>1 - Minor Note</span>
                <span>3 - Standard</span>
                <span>5 - Critical Rule</span>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn-modal-cancel"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-modal-submit"
              disabled={isSubmitting || !content.trim()}
            >
              {isSubmitting ? 'Saving...' : 'Save Memory'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

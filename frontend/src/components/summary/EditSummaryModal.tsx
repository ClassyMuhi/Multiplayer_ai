import React, { useState, useEffect } from 'react';
import { X, Sparkles, FileText } from 'lucide-react';
import { ProjectSummary } from '../../types';

interface EditSummaryModalProps {
  isOpen: boolean;
  currentSummary: ProjectSummary | null;
  onClose: () => void;
  onSaveSummary: (content: string) => Promise<void>;
}

export const EditSummaryModal: React.FC<EditSummaryModalProps> = ({
  isOpen,
  currentSummary,
  onClose,
  onSaveSummary,
}) => {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (currentSummary) {
      setContent(currentSummary.content || '');
    }
  }, [currentSummary, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      setError(null);
      await onSaveSummary(content);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to update project summary');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-dialog modal-large">
        <div className="modal-header">
          <div className="modal-title">
            <Sparkles size={18} className="modal-icon" />
            <span>Edit Project Summary</span>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="modal-alert-error">{error}</div>}

            <p className="modal-description">
              The project summary is injected into the AI agent's context during coding tasks to
              provide an immediate overview of architecture, tech stack, and goals.
            </p>

            <div className="form-group">
              <label className="form-label">Project Summary Markdown</label>
              <textarea
                className="form-textarea code-font"
                rows={12}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="# Project Overview..."
                autoFocus
              />
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
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Update Summary'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

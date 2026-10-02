import React, { useState, useEffect } from 'react';
import {
  Folder,
  Plus,
  ArrowRight,
  Sparkles,
  Terminal,
  Brain,
  Search,
  Clock,
  Layers,
  Code2,
} from 'lucide-react';
import { Project, CreateProjectPayload } from '../types';
import { apiService } from '../services/api';
import { NewProjectModal } from '../components/project/NewProjectModal';

interface ProjectsPageProps {
  onSelectProject: (project: Project) => void;
}

export const ProjectsPage: React.FC<ProjectsPageProps> = ({ onSelectProject }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getProjects();
      setProjects(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (payload: CreateProjectPayload) => {
    const newProj = await apiService.createProject(payload);
    await fetchProjects();
    onSelectProject(newProj);
  };

  const filteredProjects = projects.filter((p) => {
    const q = searchQuery.toLowerCase();
    return p.name.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q));
  });

  return (
    <div className="projects-page-container">
      {/* Hero Header */}
      <header className="projects-hero">
        <div className="hero-content">
          <div className="hero-badge">
            <Sparkles size={14} />
            <span>Multiplayer AI Coding IDE — Phase 4</span>
          </div>
          <h1>Agentic AI Coding Platform</h1>
          <p>
            Autonomous AI coding agent with persistent project memory, live terminal execution,
            and shared multiplayer workspaces.
          </p>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="projects-main">
        <div className="projects-controls-bar">
          <div className="projects-search-wrapper">
            <Search size={16} className="search-icon" />
            <input
              type="text"
              placeholder="Search workspaces..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="projects-search-input"
            />
          </div>

          <button
            className="btn-create-project"
            onClick={() => setIsModalOpen(true)}
          >
            <Plus size={16} />
            <span>New Project</span>
          </button>
        </div>

        {error && (
          <div className="projects-error-banner">
            <span>{error}</span>
            <button onClick={fetchProjects}>Retry</button>
          </div>
        )}

        {loading ? (
          <div className="projects-loading-state">
            <div className="loading-spinner" />
            <p>Loading workspaces...</p>
          </div>
        ) : (
          <div className="projects-grid">
            {/* Create Project Quick Card */}
            <div
              className="project-card create-card"
              onClick={() => setIsModalOpen(true)}
            >
              <div className="create-card-content">
                <div className="create-icon-wrapper">
                  <Plus size={24} />
                </div>
                <h3>Create Workspace</h3>
                <p>Start a new project with autonomous AI coding & persistent memory.</p>
              </div>
            </div>

            {/* List of existing projects */}
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className="project-card"
                onClick={() => onSelectProject(project)}
              >
                <div className="card-top">
                  <div className="project-icon-box">
                    <Code2 size={20} />
                  </div>
                  <span className="project-id-badge">#{project.id.slice(0, 8)}</span>
                </div>

                <div className="card-body">
                  <h3 className="project-title">{project.name}</h3>
                  <p className="project-desc">
                    {project.description || 'No description provided.'}
                  </p>
                </div>

                <div className="card-footer">
                  <div className="project-meta">
                    <span className="meta-item">
                      <Clock size={12} />
                      {project.created_at ? new Date(project.created_at).toLocaleDateString() : 'Active'}
                    </span>
                  </div>
                  <button className="btn-open-project">
                    <span>Open Workspace</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreateProject={handleCreateProject}
      />
    </div>
  );
};

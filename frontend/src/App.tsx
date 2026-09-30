import React, { useState, useEffect } from 'react';
import { Project } from './types';
import { apiService } from './services/api';
import { ProjectsPage } from './pages/ProjectsPage';
import { WorkspacePage } from './pages/WorkspacePage';

export const App: React.FC = () => {
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [loadingInitial, setLoadingInitial] = useState(true);

  // Restore project from URL hash or localStorage on first load
  useEffect(() => {
    const initProject = async () => {
      try {
        const hash = window.location.hash.replace('#/', '').replace('#', '');
        const storedProjectId = hash || localStorage.getItem('last_active_project_id');

        if (storedProjectId) {
          const project = await apiService.getProject(storedProjectId);
          if (project) {
            setActiveProject(project);
          }
        }
      } catch (err) {
        console.warn('Could not restore last project session:', err);
        localStorage.removeItem('last_active_project_id');
      } finally {
        setLoadingInitial(false);
      }
    };

    initProject();
  }, []);

  const handleSelectProject = (project: Project) => {
    setActiveProject(project);
    localStorage.setItem('last_active_project_id', project.id);
    window.location.hash = `#/projects/${project.id}`;
  };

  const handleBackToProjects = () => {
    setActiveProject(null);
    localStorage.removeItem('last_active_project_id');
    window.location.hash = '';
  };

  if (loadingInitial) {
    return (
      <div className="app-loading-screen">
        <div className="loading-spinner" />
        <p>Loading Agentic IDE Workspace...</p>
      </div>
    );
  }

  return (
    <div className="app-root">
      {activeProject ? (
        <WorkspacePage
          project={activeProject}
          onBackToProjects={handleBackToProjects}
        />
      ) : (
        <ProjectsPage onSelectProject={handleSelectProject} />
      )}
    </div>
  );
};

export default App;

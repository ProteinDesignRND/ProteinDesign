import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { ResearchDashboard } from './views/ResearchDashboard';
import { DesignStudio } from './views/DesignStudio';
import { WorkflowDesigner } from './views/WorkflowDesigner';
import { JobMonitor } from './views/JobMonitor';
import { CandidateExplorer } from './views/CandidateExplorer';
import { StructureWorkbench } from './views/StructureWorkbench';
import { ReportsProvenance } from './views/ReportsProvenance';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<ResearchDashboard />} />
          <Route path="design-studio" element={<DesignStudio />} />
          <Route path="workflow" element={<WorkflowDesigner />} />
          <Route path="jobs" element={<JobMonitor />} />
          <Route path="candidates" element={<CandidateExplorer />} />
          <Route path="structure" element={<StructureWorkbench />} />
          <Route path="reports" element={<ReportsProvenance />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;

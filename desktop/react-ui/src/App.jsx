import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import Agents from './pages/Agents'
import Skills from './pages/Skills'
import Memory from './pages/Memory'
import Research from './pages/Research'
import Chat from './pages/Chat'
import System from './pages/System'
import Settings from './pages/Settings'
import Approvals from './pages/Approvals'
import Frameworks from './pages/Frameworks'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="projects" element={<Projects />} />
          <Route path="projects/:id" element={<ProjectDetail />} />
          <Route path="agents" element={<Agents />} />
          <Route path="skills" element={<Skills />} />
          <Route path="memory" element={<Memory />} />
          <Route path="research" element={<Research />} />
          <Route path="chat" element={<Chat />} />
          <Route path="approvals" element={<Approvals />} />
          <Route path="frameworks" element={<Frameworks />} />
          <Route path="system" element={<System />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}


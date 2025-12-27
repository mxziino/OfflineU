import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { LibraryPage } from '@/pages/LibraryPage';
import { CourseDashboard } from '@/pages/CourseDashboard';
import { LearningPathDashboard } from '@/pages/LearningPathDashboard';
import { LessonView } from '@/pages/LessonView';
import { StatsPage } from '@/pages/StatsPage';
import { getCourseInfo, resetCourse } from '@/lib/api';
import type { LoadMode } from '@/components/FolderBrowser';

function AppContent() {
  const navigate = useNavigate();
  const [view, setView] = useState<'library' | 'course' | 'learning_path' | 'stats'>('library');
  const [checkingCourse, setCheckingCourse] = useState(true);

  useEffect(() => {
    // Check if there's a course already loaded
    getCourseInfo().then((data) => {
      if (data) {
        const mode = localStorage.getItem('offlineu_load_mode') as LoadMode;
        setView(mode === 'learning_path' ? 'learning_path' : 'course');
      }
      setCheckingCourse(false);
    });
  }, []);

  const handleCourseSelected = (mode: LoadMode) => {
    localStorage.setItem('offlineu_load_mode', mode);
    setView(mode === 'learning_path' ? 'learning_path' : 'course');
    navigate('/');
  };

  const handleReset = async () => {
    await resetCourse();
    localStorage.removeItem('offlineu_load_mode');
    setView('library');
    navigate('/');
  };

  const handleBackToLibrary = () => {
    setView('library');
    navigate('/');
  };

  const handleShowStats = () => {
    setView('stats');
    navigate('/stats');
  };

  if (checkingCourse) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-muted-foreground">Loading OfflineU...</div>
      </div>
    );
  }

  return (
    <Routes>
      {view === 'stats' && (
        <>
          <Route path="/stats" element={<StatsPage onBack={handleBackToLibrary} />} />
          <Route path="*" element={<Navigate to="/stats" replace />} />
        </>
      )}

      {view === 'library' && (
        <>
          <Route path="/" element={<LibraryPage onCourseSelected={handleCourseSelected} onShowStats={handleShowStats} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      )}

      {view === 'learning_path' && (
        <>
          <Route path="/" element={<LearningPathDashboard onReset={handleReset} />} />
          <Route path="/lesson/*" element={<LessonView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      )}

      {view === 'course' && (
        <>
          <Route path="/" element={<CourseDashboard onReset={handleReset} />} />
          <Route path="/lesson/*" element={<LessonView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      )}
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;

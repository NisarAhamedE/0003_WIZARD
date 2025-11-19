import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';

// Layout components
import MainLayout from './components/common/MainLayout';
import AuthLayout from './components/common/AuthLayout';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import WizardBrowserPage from './pages/WizardBrowserPage';
import WizardPlayerPage from './pages/WizardPlayerPage';
import WizardBuilderPage from './pages/admin/WizardBuilderPage';
import AnalyticsDashboardPage from './pages/admin/AnalyticsDashboardPage';
import UserManagementPage from './pages/admin/UserManagementPage';

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Protected routes */}
      <Route element={<MainLayout />}>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/wizards"
          element={
            <ProtectedRoute>
              <WizardBrowserPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/wizard/:wizardId"
          element={
            <ProtectedRoute>
              <WizardPlayerPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/wizard-builder"
          element={
            <ProtectedRoute>
              <WizardBuilderPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute>
              <UserManagementPage />
            </ProtectedRoute>
          }
        />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;

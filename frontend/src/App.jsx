import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import { isLoggedIn, currentRole } from "./lib/api";

import Login from "./pages/Login";
import Register from "./pages/Register";

import StudentDashboard from "./pages/student/Dashboard";
import StudentPreferences from "./pages/student/Preferences";
import StudentTransparency from "./pages/student/Transparency";
import StudentNotifications from "./pages/student/Notifications";

import FacultyDashboard from "./pages/faculty/Dashboard";

import AdminDashboard from "./pages/admin/Dashboard";
import AdminUpload from "./pages/admin/Upload";
import AdminAllotments from "./pages/admin/Allotments";
import AdminExperiment from "./pages/admin/Experiment";
import AdminNotify from "./pages/admin/Notify";

function HomeRedirect() {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  return <Navigate to={`/${currentRole()}/dashboard`} replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route path="/student/dashboard" element={
          <ProtectedRoute allow={["student"]}><StudentDashboard /></ProtectedRoute>
        } />
        <Route path="/student/preferences" element={
          <ProtectedRoute allow={["student"]}><StudentPreferences /></ProtectedRoute>
        } />
        <Route path="/student/transparency" element={
          <ProtectedRoute allow={["student"]}><StudentTransparency /></ProtectedRoute>
        } />
        <Route path="/student/notifications" element={
          <ProtectedRoute allow={["student"]}><StudentNotifications /></ProtectedRoute>
        } />

        <Route path="/branch_admin/dashboard" element={
          <ProtectedRoute allow={["branch_admin"]}><FacultyDashboard /></ProtectedRoute>
        } />

        <Route path="/main_admin/dashboard" element={
          <ProtectedRoute allow={["main_admin"]}><AdminDashboard /></ProtectedRoute>
        } />
        <Route path="/main_admin/upload" element={
          <ProtectedRoute allow={["main_admin"]}><AdminUpload /></ProtectedRoute>
        } />
        <Route path="/main_admin/allotments" element={
          <ProtectedRoute allow={["main_admin"]}><AdminAllotments /></ProtectedRoute>
        } />
        <Route path="/main_admin/experiment" element={
          <ProtectedRoute allow={["main_admin"]}><AdminExperiment /></ProtectedRoute>
        } />
        <Route path="/main_admin/notify" element={
          <ProtectedRoute allow={["main_admin"]}><AdminNotify /></ProtectedRoute>
        } />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
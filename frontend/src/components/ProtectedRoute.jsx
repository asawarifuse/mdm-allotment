import { Navigate } from "react-router-dom";
import { isLoggedIn, currentRole } from "../lib/api";

export default function ProtectedRoute({ children, allow }) {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  const role = currentRole();
  if (allow && !allow.includes(role)) {
    return <Navigate to={`/${role}/dashboard`} replace />;
  }
  return children;
}
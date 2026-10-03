import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, saveSession } from "../lib/api";

export default function Register() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [uid, setUid] = useState("");
  const [student, setStudent] = useState(null);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const lookup = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.get(`/auth/lookup/${uid.trim()}`);
      if (data.registered) {
        setError("UID already registered. Please login.");
        return;
      }
      setStudent(data);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || "UID not found");
    } finally {
      setLoading(false);
    }
  };

  const register = async (e) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.post("/auth/register", {
        uid: student.uid,
        password,
        confirm_password: confirm,
      });
      saveSession(data);
      navigate("/student/dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full flex items-center justify-center bg-navy-700 px-4 py-10">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-xl font-semibold text-navy-700 mb-1">Student Registration</h1>
        <p className="text-sm text-gray-500 mb-6">
          {step === 1 ? "Enter your UID to begin" : "Set your password"}
        </p>

        {error && <div className="alert-error mb-4">{error}</div>}

        {step === 1 && (
          <form onSubmit={lookup} className="space-y-4">
            <div>
              <label className="label">UID</label>
              <input
                className="input"
                value={uid}
                onChange={(e) => setUid(e.target.value)}
                required
                autoFocus
                placeholder="e.g. CSE001"
              />
            </div>
            <button className="btn-primary w-full" disabled={loading}>
              {loading ? "Looking up…" : "Continue"}
            </button>
          </form>
        )}

        {step === 2 && student && (
          <>
            <div className="bg-navy-50 rounded-md p-4 mb-5 text-sm">
              <div className="flex justify-between py-1">
                <span className="text-gray-600">Name</span>
                <span className="font-medium">{student.name}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-gray-600">CGPA</span>
                <span className="font-medium">{student.cgpa}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-gray-600">Branch</span>
                <span className="font-medium">{student.parent_branch}</span>
              </div>
            </div>

            <form onSubmit={register} className="space-y-4">
              <div>
                <label className="label">Password</label>
                <input
                  type="password"
                  className="input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                />
              </div>
              <div>
                <label className="label">Confirm Password</label>
                <input
                  type="password"
                  className="input"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  required
                  minLength={6}
                />
              </div>
              <button className="btn-primary w-full" disabled={loading}>
                {loading ? "Creating account…" : "Create Account"}
              </button>
              <button
                type="button"
                onClick={() => { setStep(1); setStudent(null); setError(""); }}
                className="btn-ghost w-full"
              >
                Back
              </button>
            </form>
          </>
        )}

        <p className="mt-5 text-sm text-center text-gray-600">
          Already registered?{" "}
          <Link to="/login" className="text-navy-700 font-medium hover:underline">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api, saveSession } from "../lib/api";

export default function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState("student");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const label = role === "student" ? "UID" : "Admin ID";

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", {
        identifier: identifier.trim(),
        password,
        role,
      });
      saveSession(data);
      navigate(`/${data.role}/dashboard`, { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full flex items-center justify-center bg-navy-700 px-4 py-10">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-6">
          <div className="w-14 h-14 mx-auto rounded-full bg-gold-500 flex items-center justify-center
                          text-navy-900 font-bold text-xl">SV</div>
          <h1 className="mt-3 text-xl font-semibold text-navy-700">MDM Allotment</h1>
          <p className="text-sm text-gray-500">St. Vincent Pallotti College</p>
        </div>

        <div className="grid grid-cols-3 gap-2 mb-5">
          {["student", "branch_admin", "main_admin"].map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRole(r)}
              className={`px-2 py-2 rounded-md text-xs font-medium border ${
                role === r
                  ? "bg-navy-700 text-white border-navy-700"
                  : "bg-white text-navy-700 border-gray-300 hover:bg-navy-50"
              }`}
            >
              {r === "student" ? "Student" : r === "branch_admin" ? "Faculty" : "Admin"}
            </button>
          ))}
        </div>

        {error && <div className="alert-error mb-4">{error}</div>}

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="label">{label}</label>
            <input
              className="input"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? "Signing in…" : "Sign In"}
          </button>
        </form>

        {role === "student" && (
          <p className="mt-5 text-sm text-center text-gray-600">
            New student?{" "}
            <Link to="/register" className="text-navy-700 font-medium hover:underline">
              Register here
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
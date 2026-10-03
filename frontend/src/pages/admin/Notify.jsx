import { useState } from "react";
import Layout from "../../components/Layout";
import { api } from "../../lib/api";

const BRANCHES = ["CSE", "CSBS", "CV", "EE", "ET", "IT", "ME", "AI", "DS", "CS", "IIOT", "RAI"];

export default function AdminNotify() {
  const tabs = [
    { to: "/main_admin/dashboard", label: "Seat Matrix" },
    { to: "/main_admin/upload", label: "Upload CSV" },
    { to: "/main_admin/allotments", label: "Master List" },
    { to: "/main_admin/experiment", label: "Fairness" },
    { to: "/main_admin/notify", label: "Notify" },
  ];

  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [target, setTarget] = useState("all");
  const [branch, setBranch] = useState("");
  const [loading, setLoading] = useState(false);
  const [ok, setOk] = useState("");
  const [error, setError] = useState("");

  const send = async (e) => {
    e.preventDefault();
    setError(""); setOk("");
    if (!title.trim() || !message.trim()) {
      setError("Title and message are required.");
      return;
    }
    setLoading(true);
    try {
      const payload = { title, message };
      if (target === "branch") payload.branch = branch;
      await api.post("/admin/notifications", payload);
      setOk("Notification sent.");
      setTitle(""); setMessage("");
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to send");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Send Notification" tabs={tabs}>
      {error && <div className="alert-error mb-4">{error}</div>}
      {ok && <div className="alert-success mb-4">{ok}</div>}

      <div className="card max-w-2xl">
        <form onSubmit={send} className="space-y-4">
          <div>
            <label className="label">Title</label>
            <input className="input" value={title}
                   onChange={(e) => setTitle(e.target.value)} maxLength={128} required />
          </div>

          <div>
            <label className="label">Message</label>
            <textarea className="input min-h-[100px]" value={message}
                      onChange={(e) => setMessage(e.target.value)} required />
          </div>

          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <label className="label">Audience</label>
              <select className="input" value={target}
                      onChange={(e) => setTarget(e.target.value)}>
                <option value="all">All students</option>
                <option value="branch">Specific branch</option>
              </select>
            </div>
            {target === "branch" && (
              <div>
                <label className="label">Branch</label>
                <select className="input" value={branch}
                        onChange={(e) => setBranch(e.target.value)} required>
                  <option value="">Select…</option>
                  {BRANCHES.map((b) => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
            )}
          </div>

          <button className="btn-primary" disabled={loading}>
            {loading ? "Sending…" : "Send Notification"}
          </button>
        </form>
      </div>
    </Layout>
  );
}
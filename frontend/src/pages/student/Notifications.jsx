import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import Spinner from "../../components/Spinner";
import { api } from "../../lib/api";

export default function StudentNotifications() {
  const tabs = [
    { to: "/student/dashboard", label: "Courses" },
    { to: "/student/preferences", label: "My Preferences" },
    { to: "/student/transparency", label: "Transparency" },
    { to: "/student/notifications", label: "Notifications" },
  ];

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const r = await api.get("/student/notifications");
      setItems(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const markRead = async (id) => {
    await api.post(`/student/notifications/${id}/read`);
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };

  return (
    <Layout title="Notifications" tabs={tabs}>
      {loading && <Spinner />}
      {error && <div className="alert-error">{error}</div>}

      {!loading && items.length === 0 && (
        <div className="card text-center text-gray-500">No notifications yet.</div>
      )}

      <div className="space-y-3">
        {items.map((n) => (
          <div
            key={n.id}
            className={`card ${!n.read ? "border-l-4 border-l-gold-500" : ""}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <div className="font-semibold text-navy-700">{n.title}</div>
                <div className="text-sm text-gray-600 mt-1">{n.message}</div>
                <div className="text-xs text-gray-400 mt-2">
                  {new Date(n.created_at).toLocaleString()} · by {n.created_by}
                  {n.branch && <> · {n.branch}</>}
                </div>
              </div>
              {!n.read && (
                <button
                  onClick={() => markRead(n.id)}
                  className="text-xs text-navy-700 hover:underline whitespace-nowrap"
                >
                  Mark read
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
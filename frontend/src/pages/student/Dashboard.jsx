import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import Spinner from "../../components/Spinner";
import { api } from "../../lib/api";

export default function StudentDashboard() {
  const tabs = [
    { to: "/student/dashboard", label: "Courses" },
    { to: "/student/preferences", label: "My Preferences" },
    { to: "/student/transparency", label: "Transparency" },
    { to: "/student/notifications", label: "Notifications" },
  ];

  const [courses, setCourses] = useState([]);
  const [prefs, setPrefs] = useState(null);
  const [myBranch, setMyBranch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [c, p, t] = await Promise.all([
          api.get("/courses"),
          api.get("/preferences/me"),
          api.get("/student/transparency"),
        ]);
        setCourses(c.data);
        setPrefs(p.data);
        setMyBranch(t.data.parent_branch);
      } catch (e) {
        setError(e.response?.data?.detail || "Failed to load");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const eligible = courses.filter((c) => c.branch_name !== myBranch);

  return (
    <Layout title="MDM Courses" tabs={tabs}>
      {loading && <Spinner />}
      {error && <div className="alert-error mb-4">{error}</div>}

      {prefs?.submitted && (
        <div className="alert-success mb-5">
          Preferences submitted and locked. Submitted at{" "}
          {new Date(prefs.submitted_at).toLocaleString()}.
        </div>
      )}

      {!loading && myBranch && (
        <p className="text-sm text-gray-600 mb-4">
          Showing MDM courses open to <b>{myBranch}</b> students (your own branch's course is excluded).
        </p>
      )}

      {!loading && eligible.length > 0 && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {eligible.map((c) => (
            <div key={c.id} className="card">
              <div className="text-xs font-medium text-gold-600 uppercase tracking-wide">
                {c.branch_name}
              </div>
              <h3 className="mt-1 font-semibold text-navy-700 leading-snug">
                {c.course_name}
              </h3>
              <div className="mt-3 text-xs text-gray-500">
                {c.total_seats} total seats
              </div>
              <a
                href={c.syllabus_pdf || "#"}
                target="_blank"
                rel="noreferrer"
                className={`mt-4 inline-block text-sm ${
                  c.syllabus_pdf
                    ? "text-navy-700 hover:underline"
                    : "text-gray-400 cursor-not-allowed"
                }`}
                onClick={(e) => !c.syllabus_pdf && e.preventDefault()}
              >
                📄 View Syllabus
              </a>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import Spinner from "../../components/Spinner";
import { api } from "../../lib/api";

const MAX_PREFS = 6;

export default function StudentPreferences() {
  const tabs = [
    { to: "/student/dashboard", label: "Courses" },
    { to: "/student/preferences", label: "My Preferences" },
    { to: "/student/transparency", label: "Transparency" },
    { to: "/student/notifications", label: "Notifications" },
  ];

  const [courses, setCourses] = useState([]);
  const [existing, setExisting] = useState(null);
  const [myBranch, setMyBranch] = useState("");
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [c, p, t] = await Promise.all([
          api.get("/courses"),
          api.get("/preferences/me"),
          api.get("/student/transparency"),
        ]);
        setCourses(c.data);
        setExisting(p.data);
        setMyBranch(t.data.parent_branch);
      } catch (e) {
        setError(e.response?.data?.detail || "Failed to load");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const eligible = courses.filter((c) => c.branch_name !== myBranch);

  const toggle = (id) => {
    setSelected((s) =>
      s.includes(id) ? s.filter((x) => x !== id) : s.length < MAX_PREFS ? [...s, id] : s
    );
  };

  const move = (idx, dir) => {
    setSelected((s) => {
      const copy = [...s];
      const j = idx + dir;
      if (j < 0 || j >= copy.length) return copy;
      [copy[idx], copy[j]] = [copy[j], copy[idx]];
      return copy;
    });
  };

  const submit = async () => {
    setError("");
    setOk("");
    if (selected.length !== MAX_PREFS) {
      setError(`Select exactly ${MAX_PREFS} courses. You selected ${selected.length}.`);
      return;
    }
    setSaving(true);
    try {
      const { data } = await api.post("/preferences", { course_ids: selected });
      setExisting(data);
      setOk("Preferences submitted and locked.");
    } catch (e) {
      setError(e.response?.data?.detail || "Submission failed");
    } finally {
      setSaving(false);
    }
  };

  const locked = existing?.submitted;
  const courseMap = Object.fromEntries(courses.map((c) => [c.id, c]));

  return (
    <Layout title="Submit Preferences" tabs={tabs}>
      {loading && <Spinner />}
      {error && <div className="alert-error mb-4">{error}</div>}
      {ok && <div className="alert-success mb-4">{ok}</div>}

      {!loading && myBranch && (
        <div className="alert-success mb-5">
          You are from <b>{myBranch}</b>. Your own branch's MDM course is hidden — MDM
          means taking another branch's course.
        </div>
      )}

      {locked && (
        <div className="card mb-6">
          <h2 className="font-semibold text-navy-700 mb-3">Your locked preferences</h2>
          <ol className="space-y-2">
            {existing.preferences.map((p) => (
              <li key={p.rank} className="flex items-center gap-3 text-sm">
                <span className="w-6 h-6 rounded-full bg-navy-700 text-white text-xs
                                 flex items-center justify-center font-medium">{p.rank}</span>
                <span className="font-medium">{p.course_name}</span>
                <span className="text-gray-500">({p.branch_name})</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {!loading && !locked && (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 grid sm:grid-cols-2 gap-3">
            {eligible.map((c) => {
              const picked = selected.includes(c.id);
              const full = !picked && selected.length >= MAX_PREFS;
              return (
                <button
                  key={c.id}
                  type="button"
                  disabled={full}
                  onClick={() => toggle(c.id)}
                  className={`text-left card transition-colors ${
                    picked ? "!border-navy-700 !bg-navy-50 ring-1 ring-navy-700" : ""
                  } ${full ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  <div className="text-xs font-medium text-gold-600 uppercase">
                    {c.branch_name}
                  </div>
                  <div className="mt-1 font-semibold text-navy-700 text-sm">
                    {c.course_name}
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    {c.total_seats} seats
                  </div>
                  {picked && (
                    <div className="mt-2 text-xs text-navy-700 font-medium">
                      Selected · Rank {selected.indexOf(c.id) + 1}
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          <div className="lg:col-span-1">
            <div className="card sticky top-4">
              <h3 className="font-semibold text-navy-700 mb-3">
                Your top {MAX_PREFS} ({selected.length}/{MAX_PREFS})
              </h3>
              {selected.length === 0 && (
                <p className="text-sm text-gray-500">Click courses to add.</p>
              )}
              <ol className="space-y-2">
                {selected.map((id, i) => (
                  <li key={id} className="flex items-center gap-2 text-sm">
                    <span className="w-6 h-6 rounded-full bg-gold-500 text-navy-900
                                     text-xs flex items-center justify-center font-medium">
                      {i + 1}
                    </span>
                    <span className="flex-1 truncate">{courseMap[id]?.course_name}</span>
                    <button onClick={() => move(i, -1)} className="text-gray-400 hover:text-navy-700">▲</button>
                    <button onClick={() => move(i, 1)} className="text-gray-400 hover:text-navy-700">▼</button>
                    <button onClick={() => toggle(id)} className="text-err hover:opacity-70">✕</button>
                  </li>
                ))}
              </ol>
              <button
                onClick={submit}
                disabled={saving || selected.length !== MAX_PREFS}
                className="btn-primary w-full mt-4"
              >
                {saving ? "Submitting…" : "Submit & Lock"}
              </button>
              <p className="mt-2 text-xs text-gray-500 text-center">
                Cannot be edited after submission.
              </p>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
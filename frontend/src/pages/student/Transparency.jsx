import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import Spinner from "../../components/Spinner";
import { api } from "../../lib/api";

export default function StudentTransparency() {
  const tabs = [
    { to: "/student/dashboard", label: "Courses" },
    { to: "/student/preferences", label: "My Preferences" },
    { to: "/student/transparency", label: "Transparency" },
    { to: "/student/notifications", label: "Notifications" },
  ];

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const r = await api.get("/student/transparency");
        setData(r.data);
      } catch (e) {
        setError(e.response?.data?.detail || "Failed to load");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <Layout title="Transparency" tabs={tabs}>
      {loading && <Spinner />}
      {error && <div className="alert-error">{error}</div>}

      {data && (
        <>
          <div className="card mb-6">
            <div className="grid sm:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-500">Your CGPA</div>
                <div className="text-xl font-semibold text-navy-700">{data.cgpa}</div>
              </div>
              <div>
                <div className="text-gray-500">Branch</div>
                <div className="text-xl font-semibold text-navy-700">{data.parent_branch}</div>
              </div>
              <div>
                <div className="text-gray-500">Your Rank</div>
                <div className="text-xl font-semibold text-navy-700">
                  #{data.rank_in_branch} / {data.total_in_branch}
                </div>
              </div>
              <div>
                <div className="text-gray-500">Allotted</div>
                <div className="text-xl font-semibold text-navy-700">
                  {data.allotted_course?.course_name || "—"}
                </div>
                {data.allotted_course?.choice_number && (
                  <div className="text-xs text-gray-500">
                    Choice #{data.allotted_course.choice_number}
                  </div>
                )}
              </div>
            </div>
          </div>

          <h2 className="font-semibold text-navy-700 mb-3">Why each preference was decided</h2>
          <div className="space-y-3">
            {data.preference_details.map((d) => (
              <div
                key={d.rank}
                className={`card border-l-4 ${
                  d.you_got_this ? "border-l-ok" : "border-l-gray-300"
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="w-7 h-7 rounded-full bg-navy-700 text-white text-xs
                                   flex items-center justify-center font-medium flex-shrink-0">
                    {d.rank}
                  </span>
                  <div className="flex-1">
                    <div className="font-semibold text-navy-700">{d.course_name}</div>
                    <div className="text-xs text-gray-500">Offered by {d.offering_branch}</div>
                    <div className="mt-2 grid sm:grid-cols-3 gap-2 text-xs text-gray-600">
                      <div>Seats for your branch: <b>{d.seats_for_your_branch}</b></div>
                      <div>Admitted: <b>{d.admitted_from_your_branch}</b></div>
                      <div>
                        Cutoff CGPA: <b>{d.cutoff_cgpa ?? "—"}</b>
                      </div>
                    </div>
                    <div className={`mt-2 text-sm ${
                      d.you_got_this ? "text-ok font-medium" : "text-gray-600"
                    }`}>
                      {d.explanation}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </Layout>
  );
}
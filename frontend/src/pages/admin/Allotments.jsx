import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import Spinner from "../../components/Spinner";
import { api } from "../../lib/api";

export default function AdminAllotments() {
  const tabs = [
    { to: "/main_admin/dashboard", label: "Seat Matrix" },
    { to: "/main_admin/upload", label: "Upload CSV" },
    { to: "/main_admin/allotments", label: "Master List" },
    { to: "/main_admin/experiment", label: "Fairness" },
    { to: "/main_admin/notify", label: "Notify" },
  ];

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const r = await api.get("/admin/allotments");
        setRows(r.data);
      } catch (e) {
        setError(e.response?.data?.detail || "Failed to load");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const filtered = rows.filter((r) =>
    !q ||
    r.uid.toLowerCase().includes(q.toLowerCase()) ||
    r.name.toLowerCase().includes(q.toLowerCase()) ||
    r.course_name.toLowerCase().includes(q.toLowerCase()) ||
    r.parent_branch.toLowerCase().includes(q.toLowerCase())
  );

  const exportFile = async (kind) => {
    const token = localStorage.getItem("token");
    const url = `${api.defaults.baseURL}/admin/export/${kind}`;
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `allotments.${kind === "excel" ? "xlsx" : "pdf"}`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <Layout title="Master Allotment List" tabs={tabs}>
      {loading && <Spinner />}
      {error && <div className="alert-error mb-4">{error}</div>}

      <div className="flex flex-wrap gap-3 mb-4">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search by UID, name, course, branch…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button className="btn-ghost" onClick={() => exportFile("excel")}>⬇ Excel</button>
        <button className="btn-ghost" onClick={() => exportFile("pdf")}>⬇ PDF</button>
      </div>

      <div className="card overflow-x-auto">
        <div className="text-sm text-gray-500 mb-3">
          {filtered.length} of {rows.length} allotments
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="py-2">UID</th>
              <th>Name</th>
              <th>CGPA</th>
              <th>Branch</th>
              <th>Course</th>
              <th>Offered By</th>
              <th>Choice</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.uid} className="border-b last:border-0">
                <td className="py-2 font-medium">{r.uid}</td>
                <td>{r.name}</td>
                <td>{r.cgpa}</td>
                <td>{r.parent_branch}</td>
                <td>{r.course_name}</td>
                <td>{r.offering_branch}</td>
                <td>
                  <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                    r.choice_number
                      ? "bg-navy-50 text-navy-700"
                      : "bg-amber-50 text-amber-700"
                  }`}>
                    {r.choice_number ? `#${r.choice_number}` : "Fallback"}
                  </span>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={7} className="py-6 text-center text-gray-500">
                No allotments match.
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
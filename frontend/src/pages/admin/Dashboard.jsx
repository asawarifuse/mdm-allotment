import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import Spinner from "../../components/Spinner";
import { api } from "../../lib/api";

export default function AdminDashboard() {
  const [matrix, setMatrix] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [running, setRunning] = useState(false);

  const tabs = [
    { to: "/main_admin/dashboard", label: "Seat Matrix" },
    { to: "/main_admin/upload", label: "Upload CSV" },
    { to: "/main_admin/allotments", label: "Master List" },
    { to: "/main_admin/experiment", label: "Fairness" },
    { to: "/main_admin/notify", label: "Notify" },
  ];

  const load = async () => {
    setLoading(true);
    try {
      const r = await api.get("/admin/seat-matrix");
      setMatrix(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const updateSeat = async (courseId, branch, seats) => {
    setError(""); setOk("");
    try {
      await api.put(`/admin/seats/${courseId}/${branch}?seats=${seats}`);
      setOk(`Updated ${branch} → ${seats} seats for course #${courseId}.`);
      load();
    } catch (e) {
      setError(e.response?.data?.detail || "Update failed");
    }
  };

  const runAllotment = async () => {
    if (!window.confirm("Run college-wide allotment? This will overwrite previous results.")) return;
    setRunning(true); setError(""); setOk("");
    try {
      const r = await api.post("/allotment/run/college");
      setOk(`Allotted ${r.data.allotted} students. Unallotted: ${r.data.unallotted.length}`);
      load();
    } catch (e) {
      setError(e.response?.data?.detail || "Allotment failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <Layout title="Admin Dashboard" tabs={tabs}>
      {loading && <Spinner />}
      {error && <div className="alert-error mb-4">{error}</div>}
      {ok && <div className="alert-success mb-4">{ok}</div>}

      <div className="flex gap-3 mb-5 flex-wrap">
        <button onClick={runAllotment} disabled={running} className="btn-gold">
          {running ? "Running…" : "Run College-Wide Allotment"}
        </button>
        <a href={`${api.defaults.baseURL}/admin/export/excel`} className="btn-ghost"
           onClick={(e) => { e.preventDefault(); exportFile("excel"); }}>
          ⬇ Excel
        </a>
        <a href="#" className="btn-ghost"
           onClick={(e) => { e.preventDefault(); exportFile("pdf"); }}>
          ⬇ PDF
        </a>
      </div>

      {matrix && (
        <div className="card overflow-x-auto">
          <h2 className="font-semibold text-navy-700 mb-4">Seat Matrix (per course per branch)</h2>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 sticky left-0 bg-white">Course \\ Branch</th>
                {matrix.branches.map((b) => (
                  <th key={b} className="px-2 py-2 text-center font-medium text-navy-700">{b}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.courses.map((c) => (
                <tr key={c.course_id} className="border-b last:border-0">
                  <td className="py-2 pr-3 sticky left-0 bg-white">
                    <div className="font-medium text-navy-700">{c.course_name}</div>
                    <div className="text-gray-500 text-[10px]">{c.offering_branch}</div>
                  </td>
                  {matrix.branches.map((b) => {
                    const cell = matrix.cells.find(
                      (x) => x.course_id === c.course_id && x.branch === b
                    );
                    return (
                      <td key={b} className="px-1 py-1 text-center">
                        {cell ? (
                          <CellEditor
                            cell={cell}
                            onSave={(val) => updateSeat(c.course_id, b, val)}
                          />
                        ) : (
                          <span className="text-gray-300">—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-xs text-gray-500 mt-3">
            Click a number to edit. Changes are locked once allotment starts.
          </p>
        </div>
      )}
    </Layout>
  );
}

function CellEditor({ cell, onSave }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(cell.seats);

  if (!editing) {
    return (
      <button
        onClick={() => { setEditing(true); setValue(cell.seats); }}
        className="px-2 py-1 rounded hover:bg-navy-50 text-navy-700 font-medium"
        title={`Filled: ${cell.filled_seats} / ${cell.seats}`}
      >
        {cell.seats}
      </button>
    );
  }

  return (
    <div className="flex items-center gap-1">
      <input
        type="number"
        min="0"
        autoFocus
        className="w-14 px-1 py-0.5 border rounded text-center"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") { onSave(value); setEditing(false); }
          if (e.key === "Escape") setEditing(false);
        }}
      />
      <button onClick={() => { onSave(value); setEditing(false); }}
              className="text-ok">✓</button>
      <button onClick={() => setEditing(false)} className="text-err">✕</button>
    </div>
  );
}

async function exportFile(kind) {
  const token = localStorage.getItem("token");
  const url = `${api.defaults.baseURL}/admin/export/${kind}`;
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  const blob = await res.blob();
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `allotments.${kind === "excel" ? "xlsx" : "pdf"}`;
  a.click();
  URL.revokeObjectURL(a.href);
}
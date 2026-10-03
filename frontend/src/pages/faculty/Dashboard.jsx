import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import Spinner from "../../components/Spinner";
import { api } from "../../lib/api";

export default function FacultyDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [running, setRunning] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const r = await api.get("/faculty/dashboard");
      setData(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const updateSeat = async (branch, seats) => {
    setError(""); setOk("");
    try {
      await api.put("/faculty/seats", { branch, seats: Number(seats) });
      setOk(`Updated ${branch} to ${seats} seats.`);
      load();
    } catch (e) {
      setError(e.response?.data?.detail || "Update failed");
    }
  };

  const runAllotment = async () => {
    if (!window.confirm("Run allotment for your course?")) return;
    setRunning(true); setError(""); setOk("");
    try {
      const r = await api.post("/allotment/run/course");
      setOk(`Allotted ${r.data.allotted} students. Unallotted: ${r.data.unallotted.length}`);
      load();
    } catch (e) {
      setError(e.response?.data?.detail || "Allotment failed");
    } finally {
      setRunning(false);
    }
  };

  const tabs = [{ to: "/branch_admin/dashboard", label: "My Course" }];

  return (
    <Layout title="Faculty Dashboard" tabs={tabs}>
      {loading && <Spinner />}
      {error && <div className="alert-error mb-4">{error}</div>}
      {ok && <div className="alert-success mb-4">{ok}</div>}

      {data && (
        <>
          <div className="card mb-6">
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <div className="text-xs font-medium text-gold-600 uppercase">
                  {data.branch_name}
                </div>
                <h2 className="text-xl font-semibold text-navy-700">{data.course_name}</h2>
              </div>
              <button
                onClick={runAllotment}
                disabled={running}
                className="btn-gold"
              >
                {running ? "Running…" : "Run Allotment for This Course"}
              </button>
            </div>
          </div>

          <h3 className="font-semibold text-navy-700 mb-3">Seat quotas by branch</h3>
          <div className="card overflow-x-auto mb-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="py-2">Branch</th>
                  <th>Seats</th>
                  <th>Filled</th>
                  <th>Available</th>
                  <th>Edit</th>
                </tr>
              </thead>
              <tbody>
                {data.seats_by_branch.map((s) => (
                  <SeatRow key={s.branch} row={s} onSave={updateSeat} />
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="font-semibold text-navy-700 mb-3">
            Students who selected your course ({data.students_selected.length})
          </h3>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="py-2">UID</th>
                  <th>Name</th>
                  <th>CGPA</th>
                  <th>Branch</th>
                  <th>Preference Rank</th>
                </tr>
              </thead>
              <tbody>
                {data.students_selected.map((s) => (
                  <tr key={s.uid} className="border-b last:border-0">
                    <td className="py-2 font-medium">{s.uid}</td>
                    <td>{s.name}</td>
                    <td>{s.cgpa}</td>
                    <td>{s.parent_branch}</td>
                    <td>
                      <span className="inline-block px-2 py-0.5 rounded-full bg-navy-50
                                       text-navy-700 text-xs font-medium">
                        #{s.rank}
                      </span>
                    </td>
                  </tr>
                ))}
                {data.students_selected.length === 0 && (
                  <tr><td colSpan={5} className="py-4 text-center text-gray-500">
                    No students selected your course yet.
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </Layout>
  );
}

function SeatRow({ row, onSave }) {
  const [value, setValue] = useState(row.seats);
  const changed = Number(value) !== row.seats;
  return (
    <tr className="border-b last:border-0">
      <td className="py-2 font-medium">{row.branch}</td>
      <td>
        <input
          type="number"
          min="0"
          className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      </td>
      <td>{row.filled_seats}</td>
      <td>{row.available}</td>
      <td>
        <button
          disabled={!changed}
          onClick={() => onSave(row.branch, value)}
          className="btn-primary !py-1 !px-3 !text-xs"
        >
          Save
        </button>
      </td>
    </tr>
  );
}
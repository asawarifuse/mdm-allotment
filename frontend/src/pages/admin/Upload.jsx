import { useState } from "react";
import Layout from "../../components/Layout";
import { api } from "../../lib/api";

export default function AdminUpload() {
  const tabs = [
    { to: "/main_admin/dashboard", label: "Seat Matrix" },
    { to: "/main_admin/upload", label: "Upload CSV" },
    { to: "/main_admin/allotments", label: "Master List" },
    { to: "/main_admin/experiment", label: "Fairness" },
    { to: "/main_admin/notify", label: "Notify" },
  ];

  const [kind, setKind] = useState("students");
  const [mode, setMode] = useState("skip");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    if (!file) { setError("Choose a CSV file."); return; }
    setLoading(true); setError(""); setResult(null);

    const form = new FormData();
    form.append("file", file);
    if (kind === "students") form.append("mode", mode);

    try {
      const r = await api.post(
        kind === "students" ? "/admin/upload-students" : "/admin/upload-admins",
        form
      );
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const downloadCredentials = async (branch) => {
    const token = localStorage.getItem("token");
    const url = branch
      ? `${api.defaults.baseURL}/admin/credentials/${branch}`
      : `${api.defaults.baseURL}/admin/credentials-all`;
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = branch ? `${branch}_credentials.csv` : "credentials_all.zip";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <Layout title="Upload CSV" tabs={tabs}>
      {error && <div className="alert-error mb-4">{error}</div>}

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-navy-700 mb-4">Upload</h2>

          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setKind("students")}
              className={kind === "students" ? "btn-primary" : "btn-ghost"}
            >
              Students
            </button>
            <button
              onClick={() => setKind("admins")}
              className={kind === "admins" ? "btn-primary" : "btn-ghost"}
            >
              Branch Admins
            </button>
          </div>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="label">CSV file</label>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setFile(e.target.files[0])}
                className="input"
              />
            </div>

            {kind === "students" && (
              <div>
                <label className="label">Duplicate handling</label>
                <select value={mode} onChange={(e) => setMode(e.target.value)} className="input">
                  <option value="skip">Skip existing UIDs (safest)</option>
                  <option value="update">Update name/CGPA/contact for existing</option>
                  <option value="abort">Abort if any UID exists</option>
                </select>
              </div>
            )}

            <button className="btn-primary w-full" disabled={loading}>
              {loading ? "Uploading…" : "Upload"}
            </button>
          </form>

          <div className="mt-6 text-xs text-gray-500 space-y-1">
            <p><b>Students CSV columns:</b></p>
            <code className="block bg-gray-50 p-2 rounded text-[11px]">
              UID, Name of the students, CGPA (As per the I semester), Contact number, Name of the Parent Branch
            </code>
            <p className="pt-2"><b>Branch admins CSV columns:</b></p>
            <code className="block bg-gray-50 p-2 rounded text-[11px]">
              admin_id, name, branch, password
            </code>
          </div>
        </div>

        <div className="card">
          <h2 className="font-semibold text-navy-700 mb-4">Result</h2>

          {!result && <p className="text-sm text-gray-500">Upload a file to see results here.</p>}

          {result && (
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-3 gap-3">
                <Stat label="Inserted" value={result.inserted} />
                <Stat label="Updated" value={result.updated ?? 0} />
                <Stat label="Skipped" value={result.skipped ?? 0} />
              </div>
              {result.errors?.length > 0 && (
                <div className="alert-error text-xs">
                  {result.errors.slice(0, 5).map((e, i) => <div key={i}>{e}</div>)}
                  {result.errors.length > 5 && <div>…and {result.errors.length - 5} more</div>}
                </div>
              )}
              {result.credentials?.length > 0 && (
                <div>
                  <p className="text-xs text-gray-600 mb-2">
                    ⚠ Passwords shown once. Download the per-branch CSV now.
                  </p>
                  <button onClick={() => downloadCredentials(null)} className="btn-gold w-full">
                    ⬇ Download All Branches (ZIP)
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

function Stat({ label, value }) {
  return (
    <div className="bg-navy-50 rounded-md p-3 text-center">
      <div className="text-2xl font-semibold text-navy-700">{value}</div>
      <div className="text-xs text-gray-600">{label}</div>
    </div>
  );
}
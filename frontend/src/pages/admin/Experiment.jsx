import { useState } from "react";
import Layout from "../../components/Layout";
import { api } from "../../lib/api";

export default function AdminExperiment() {
  const tabs = [
    { to: "/main_admin/dashboard", label: "Seat Matrix" },
    { to: "/main_admin/upload", label: "Upload CSV" },
    { to: "/main_admin/allotments", label: "Master List" },
    { to: "/main_admin/experiment", label: "Fairness" },
    { to: "/main_admin/notify", label: "Notify" },
  ];

  const [seed, setSeed] = useState(42);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const r = await api.post(`/admin/experiment/fairness?seed=${seed}`);
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Experiment failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Fairness Experiment" tabs={tabs}>
      {error && <div className="alert-error mb-4">{error}</div>}

      <div className="card mb-6">
        <p className="text-sm text-gray-600 mb-4">
          Simulates the current student pool three ways: <b>CGPA-priority</b>,{" "}
          <b>Random lottery</b>, and <b>Hybrid (rank-sum)</b>. Read-only — does not
          alter live allotments. Report includes chi-square test on choice distribution.
        </p>
        <div className="flex gap-3 items-end flex-wrap">
          <div>
            <label className="label">Seed (for reproducibility)</label>
            <input
              type="number"
              className="input w-32"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
            />
          </div>
          <button onClick={run} disabled={loading} className="btn-gold">
            {loading ? "Running…" : "Run Comparison"}
          </button>
        </div>
      </div>

      {result && (
        <>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <ModeCard title="CGPA (current)" data={result.cgpa} accent />
            <ModeCard title="Lottery" data={result.lottery} />
            <ModeCard title="Hybrid" data={result.hybrid} />
          </div>

          <div className="card">
            <h3 className="font-semibold text-navy-700 mb-3">Statistical Summary</h3>
            <div className="grid sm:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-500">Chi-square p-value</div>
                <div className="text-xl font-semibold text-navy-700">{result.p_value}</div>
              </div>
              <div>
                <div className="text-gray-500">Cramér's V (effect size)</div>
                <div className="text-xl font-semibold text-navy-700">{result.cramers_v}</div>
              </div>
              <div>
                <div className="text-gray-500">Interpretation</div>
                <div className={`text-sm font-medium mt-1 ${
                  result.p_value < 0.05 ? "text-ok" : "text-gray-600"
                }`}>
                  {result.interpretation}
                </div>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-4">
              p &lt; 0.05 means the three allocation strategies produce statistically
              different student outcomes — this is the finding for publication.
            </p>
          </div>
        </>
      )}
    </Layout>
  );
}

function ModeCard({ title, data, accent }) {
  return (
    <div className={`card ${accent ? "ring-2 ring-gold-500" : ""}`}>
      <h3 className="font-semibold text-navy-700 mb-3">{title}</h3>
      <ul className="space-y-2 text-sm">
        <Metric label="Got 1st choice" value={`${data.first_choice_pct}%`} />
        <Metric label="Got 2nd choice" value={`${data.second_choice_pct}%`} />
        <Metric label="Got 5th choice" value={`${data.fifth_choice_pct}%`} />
        <Metric label="Fallback" value={`${data.fallback_pct}%`} />
        <Metric label="Unallotted" value={`${data.unallotted_pct}%`} />
      </ul>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <li className="flex justify-between">
      <span className="text-gray-600">{label}</span>
      <span className="font-medium text-navy-700">{value}</span>
    </li>
  );
}
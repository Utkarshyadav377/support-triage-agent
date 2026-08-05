import { useEffect, useState } from "react";
import axios from "axios";


interface Metrics {
  total_tickets: number;
  avg_latency_ms: number;
  total_cost_usd: number;
  error_rate: number;
  escalation_rate: number;
  recent: any[];
}
const API_URL = import.meta.env.VITE_API_URL || "https://support-triage-agent-lerr.onrender.com/";
function App() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [ticketText, setTicketText] = useState("");
  const [result, setResult] = useState<any>(null);

  const fetchMetrics = async () => {
    const res = await axios.get(`${API_URL}/metrics`);
    setMetrics(res.data);
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const submitTicket = async () => {
    const res = await axios.post(`${API_URL}/triage`, { text: ticketText });
    setResult(res.data);
    fetchMetrics();
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: 900, margin: "0 auto" }}>
      <h1>Support Triage Agent — Ops Dashboard</h1>

      {metrics && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", margin: "1.5rem 0" }}>
          <Card label="Total Tickets" value={metrics.total_tickets} />
          <Card label="Avg Latency" value={`${metrics.avg_latency_ms} ms`} />
          <Card label="Total Cost" value={`$${metrics.total_cost_usd}`} />
          <Card label="Escalation Rate" value={`${(metrics.escalation_rate * 100).toFixed(1)}%`} />
        </div>
      )}

      <div style={{ margin: "2rem 0" }}>
        <textarea
          value={ticketText}
          onChange={(e) => setTicketText(e.target.value)}
          placeholder="Paste a support ticket..."
          style={{ width: "100%", height: 100, padding: 8 }}
        />
        <button onClick={submitTicket} style={{ marginTop: 8, padding: "8px 16px" }}>
          Triage Ticket
        </button>
      </div>

      {result && (
        <div style={{ background: "#f5f5f5", padding: 16, borderRadius: 8 }}>
          <p><strong>Category:</strong> {result.category} ({(result.confidence * 100).toFixed(0)}% confidence)</p>
          <p><strong>Escalate:</strong> {result.escalate ? "Yes" : "No"}</p>
          <p><strong>Draft reply:</strong> {result.draft_reply}</p>
        </div>
      )}

      {metrics && (
        <table style={{ width: "100%", marginTop: "2rem", borderCollapse: "collapse" }}>
          <thead>
            <tr><th>ID</th><th>Category</th><th>Confidence</th><th>Escalated</th><th>Latency</th><th>Cost</th></tr>
          </thead>
          <tbody>
            {metrics.recent.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td><td>{r.category}</td><td>{r.confidence}</td>
                <td>{r.escalated ? "⚠️" : "—"}</td><td>{r.latency_ms}ms</td><td>${r.cost_usd}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
      <div style={{ fontSize: 12, color: "#666" }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 600 }}>{value}</div>
    </div>
  );
}

export default App;
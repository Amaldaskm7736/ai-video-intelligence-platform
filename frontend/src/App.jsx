import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { AlertTriangle, Camera, Shield, Activity } from "lucide-react";

const API = "http://localhost:8000";

export default function App() {
  const [incidents, setIncidents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  // Fetch incidents from backend
  const fetchIncidents = async () => {
    try {
      const res = await axios.get(`${API}/incidents/`, { params: { limit: 20 } });
      setIncidents(res.data);

      // Build stats from incidents
      const classCounts = {};
      res.data.forEach(inc => {
        classCounts[inc.object_class] = (classCounts[inc.object_class] || 0) + 1;
      });
      setStats(classCounts);
    } catch (e) {
      console.error("Failed to fetch incidents:", e);
    }
  };

  // Connect to WebSocket for live alerts
  useEffect(() => {
    fetchIncidents();

    const ws = new WebSocket(`ws://localhost:8000/alerts/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      console.log("WebSocket connected!");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "alert") {
        setAlerts(prev => [data, ...prev].slice(0, 10));
        fetchIncidents(); // refresh incident list
      }
    };

    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    // Refresh incidents every 10 seconds
    const interval = setInterval(fetchIncidents, 10000);

    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, []);

  // Build chart data
  const chartData = Object.entries(stats).map(([name, count]) => ({ name, count }));

  return (
    <div style={{ minHeight: "100vh", background: "#0f1117", color: "#fff", fontFamily: "sans-serif", padding: "20px" }}>
      
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Shield size={32} color="#00ff88" />
          <h1 style={{ margin: 0, fontSize: "24px" }}>AI Video Intelligence Platform</h1>
        </div>
        <div style={{
          padding: "6px 16px", borderRadius: "20px",
          background: connected ? "#00ff8820" : "#ff000020",
          border: `1px solid ${connected ? "#00ff88" : "#ff0000"}`,
          color: connected ? "#00ff88" : "#ff0000",
          fontSize: "14px"
        }}>
          {connected ? "● Live" : "○ Disconnected"}
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "24px" }}>
        {[
          { label: "Total Incidents", value: incidents.length, icon: <Activity size={20} />, color: "#00ff88" },
          { label: "Live Alerts", value: alerts.length, icon: <AlertTriangle size={20} />, color: "#ff4444" },
          { label: "Object Classes", value: Object.keys(stats).length, icon: <Camera size={20} />, color: "#4488ff" },
          { label: "Active Zones", value: 1, icon: <Shield size={20} />, color: "#ffaa00" },
        ].map((card, i) => (
          <div key={i} style={{
            background: "#1a1d27", borderRadius: "12px", padding: "20px",
            border: `1px solid ${card.color}30`
          }}>
            <div style={{ color: card.color, marginBottom: "8px" }}>{card.icon}</div>
            <div style={{ fontSize: "28px", fontWeight: "bold", color: card.color }}>{card.value}</div>
            <div style={{ fontSize: "13px", color: "#888" }}>{card.label}</div>
          </div>
        ))}
      </div>

      {/* Main Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>

        {/* Live Alerts */}
        <div style={{ background: "#1a1d27", borderRadius: "12px", padding: "20px", border: "1px solid #ff444430" }}>
          <h2 style={{ margin: "0 0 16px 0", fontSize: "16px", color: "#ff4444", display: "flex", alignItems: "center", gap: "8px" }}>
            <AlertTriangle size={18} /> Live Alerts
          </h2>
          {alerts.length === 0 ? (
            <p style={{ color: "#555", fontSize: "14px" }}>No alerts yet — trigger the red zone!</p>
          ) : (
            alerts.map((alert, i) => (
              <div key={i} style={{
                padding: "10px", marginBottom: "8px", borderRadius: "8px",
                background: "#ff444415", border: "1px solid #ff444440",
                fontSize: "13px"
              }}>
                <span style={{ color: "#ff4444", fontWeight: "bold" }}>🚨 ALERT </span>
                <span style={{ color: "#fff" }}>{alert.object_class} #{alert.object_id}</span>
                <span style={{ color: "#888" }}> entered </span>
                <span style={{ color: "#ffaa00" }}>{alert.zone_name}</span>
                <div style={{ color: "#555", fontSize: "11px", marginTop: "4px" }}>{alert.timestamp}</div>
              </div>
            ))
          )}
        </div>

        {/* Analytics Chart */}
        <div style={{ background: "#1a1d27", borderRadius: "12px", padding: "20px", border: "1px solid #4488ff30" }}>
          <h2 style={{ margin: "0 0 16px 0", fontSize: "16px", color: "#4488ff", display: "flex", alignItems: "center", gap: "8px" }}>
            <Activity size={18} /> Detections by Class
          </h2>
          {chartData.length === 0 ? (
            <p style={{ color: "#555", fontSize: "14px" }}>No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#888" fontSize={12} />
                <YAxis stroke="#888" fontSize={12} />
                <Tooltip contentStyle={{ background: "#1a1d27", border: "1px solid #333" }} />
                <Bar dataKey="count" fill="#4488ff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Incident History Table */}
      <div style={{ background: "#1a1d27", borderRadius: "12px", padding: "20px", border: "1px solid #ffffff15" }}>
        <h2 style={{ margin: "0 0 16px 0", fontSize: "16px", color: "#fff", display: "flex", alignItems: "center", gap: "8px" }}>
          <Camera size={18} /> Incident History
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ color: "#888", borderBottom: "1px solid #333" }}>
              {["ID", "Class", "Track ID", "Zone", "Confidence", "Timestamp"].map(h => (
                <th key={h} style={{ padding: "8px", textAlign: "left" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {incidents.map((inc, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #222" }}>
                <td style={{ padding: "8px", color: "#555" }}>#{inc.id}</td>
                <td style={{ padding: "8px" }}>
                  <span style={{
                    padding: "2px 8px", borderRadius: "12px",
                    background: "#4488ff20", color: "#4488ff", fontSize: "12px"
                  }}>{inc.object_class}</span>
                </td>
                <td style={{ padding: "8px", color: "#00ff88" }}>#{inc.object_id}</td>
                <td style={{ padding: "8px", color: "#ffaa00" }}>{inc.zone_name}</td>
                <td style={{ padding: "8px", color: "#888" }}>{(inc.confidence * 100).toFixed(0)}%</td>
                <td style={{ padding: "8px", color: "#555" }}>{new Date(inc.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
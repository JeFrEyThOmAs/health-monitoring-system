import { useEffect, useState } from "react";

function App() {
  const [monitoring, setMonitoring] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [sessionId, setSessionId] = useState(null);

  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // Start monitoring
  const startMonitoring = async () => {
    try {
      setError("");
      setResult(null);
      setSessionId(null);

      const response = await fetch(
        "http://127.0.0.1:8000/start-monitoring",
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to start monitoring");
      }

      setMonitoring(true);
      setTimeLeft(60);

    } catch (err) {
      setError(err.message);
    }
  };

  // Countdown timer
  useEffect(() => {
    if (!monitoring || timeLeft <= 0) {
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((previous) => previous - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [monitoring, timeLeft]);

  // Check backend monitoring status
  useEffect(() => {
    if (!monitoring) {
      return;
    }

    const checkStatus = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/monitoring-status"
        );

        const data = await response.json();

        if (!data.running) {
          setMonitoring(false);
          setTimeLeft(0);
          setSessionId(data.session_id);
        }

      } catch (err) {
        console.error(err);
      }
    };

    const interval = setInterval(checkStatus, 1000);

    return () => clearInterval(interval);
  }, [monitoring]);

  // Analyze data
  const analyzeData = async () => {
    try {
      setAnalyzing(true);
      setError("");

      const response = await fetch(
        "http://127.0.0.1:8000/analyze"
      );

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const data = await response.json();

      setResult(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fa",
        padding: "40px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "700px",
          margin: "auto",
          background: "white",
          padding: "30px",
          borderRadius: "15px",
          boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
        }}
      >
        <h1 style={{ textAlign: "center" }}>
          ❤️ Health Monitor
        </h1>

        <p style={{ textAlign: "center", color: "#666" }}>
          Heart Rate & SpO₂ Monitoring
        </p>

        {/* Start Button */}

        {!monitoring && !sessionId && (
          <button
            onClick={startMonitoring}
            style={{
              width: "100%",
              padding: "15px",
              fontSize: "18px",
              cursor: "pointer",
              borderRadius: "8px",
              border: "none",
              background: "#2563eb",
              color: "white",
            }}
          >
            START MONITORING
          </button>
        )}

        {/* Monitoring */}

        {monitoring && (
          <div style={{ textAlign: "center", marginTop: "30px" }}>
            <h2>Monitoring in progress...</h2>

            <div
              style={{
                fontSize: "60px",
                fontWeight: "bold",
                margin: "20px",
              }}
            >
              {timeLeft}s
            </div>

            <p>
              Please keep your finger on the sensor.
            </p>

            <p style={{ color: "#666" }}>
              Collecting heart-rate and SpO₂ data...
            </p>
          </div>
        )}

        {/* Analyze Button */}

        {!monitoring && sessionId && !result && (
          <div style={{ marginTop: "30px", textAlign: "center" }}>
            <p>
              ✅ Monitoring completed
            </p>

            <p>
              Session ID: {sessionId}
            </p>

            <button
              onClick={analyzeData}
              disabled={analyzing}
              style={{
                width: "100%",
                padding: "15px",
                fontSize: "18px",
                cursor: "pointer",
                borderRadius: "8px",
                border: "none",
                background: "#16a34a",
                color: "white",
              }}
            >
              {analyzing ? "ANALYZING..." : "ANALYZE DATA"}
            </button>
          </div>
        )}

        {/* Error */}

        {error && (
          <div
            style={{
              marginTop: "20px",
              padding: "15px",
              background: "#fee2e2",
              color: "#991b1b",
              borderRadius: "8px",
            }}
          >
            {error}
          </div>
        )}

        {/* Analysis Result */}

        {result && (
          <div style={{ marginTop: "30px" }}>
            <h2>📊 Analysis Result</h2>

            <p>
              <strong>Session:</strong> {result.session_id}
            </p>

            <p>
              <strong>Readings:</strong> {result.reading_count}
            </p>

            <hr />

            <h3>❤️ Heart Rate</h3>

            <p>
              Average: {result.heart_rate.average} BPM
            </p>

            <p>
              Minimum: {result.heart_rate.minimum} BPM
            </p>

            <p>
              Maximum: {result.heart_rate.maximum} BPM
            </p>

            <h3>🫁 SpO₂</h3>

            <p>
              Average: {result.spo2.average}%
            </p>

            <p>
              Minimum: {result.spo2.minimum}%
            </p>

            <h3>💡 Insight</h3>

            <p>{result.insight}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
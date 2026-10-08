import { useState } from "react";

function App() {

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeData = async () => {

    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/analyze"
      );

      const data = await response.json();

      setAnalysis(data);

    } catch (error) {

      console.error(error);

      alert("Could not connect to backend.");

    } finally {

      setLoading(false);

    }
  };


  return (
    <div>

      <h1>❤️ Health Monitor</h1>

      <button onClick={analyzeData}>
        {loading ? "Analyzing..." : "ANALYZE DATA"}
      </button>


      {analysis && (

        <div>

          <h2>Analysis Result</h2>

          <p>
            Session ID: {analysis.session_id}
          </p>

          <p>
            Readings: {analysis.reading_count}
          </p>


          <h3>Heart Rate</h3>

          <p>
            Average: {analysis.heart_rate.average} BPM
          </p>

          <p>
            Minimum: {analysis.heart_rate.minimum} BPM
          </p>

          <p>
            Maximum: {analysis.heart_rate.maximum} BPM
          </p>


          <h3>SpO₂</h3>

          <p>
            Average: {analysis.spo2.average}%
          </p>

          <p>
            Minimum: {analysis.spo2.minimum}%
          </p>


          <h3>Insight</h3>

          <p>
            {analysis.insight}
          </p>

        </div>

      )}

    </div>
  );
}

export default App;
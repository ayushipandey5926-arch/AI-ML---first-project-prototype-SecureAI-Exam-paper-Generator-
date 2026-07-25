import { useState } from "react";

export default function App() {
  const [selectedExam, setSelectedExam] = useState("NEET");
  const [loading, setLoading] = useState(false);
  const [paper, setPaper] = useState(null);
  const [error, setError] = useState("");
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setPaper(null);
    setAnswers({});
    setSubmitted(false);
    setScore(null);

    try {
      const res = await fetch("/api/generate-paper", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
        },
        body: JSON.stringify({
          examType: selectedExam,
          topic: "biology",
          difficulty: "medium",
          numQuestions: 10,
        }),
      });

      const data = await res.json();
      console.log("API data:", data);

      if (!res.ok) {
        setError(JSON.stringify(data));
      } else {
        setPaper(data);
      }
    } catch (err) {
      console.error("Fetch error:", err);
      setError(err.message || "Backend connection failed");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (qid, option) => {
    setAnswers((prev) => ({ ...prev, [qid]: option }));
  };

  const handleSubmitPaper = (e) => {
    e.preventDefault();
    if (!paper?.questions?.length) return;

    let correct = 0;

    paper.questions.forEach((q, index) => {
      const key = `${q.question_no}-${index}`;
      const selected = answers[key];

      const map = { a: 0, b: 1, c: 2, d: 3 };
      const correctIndex = map[String(q.answer).toLowerCase()];
      const correctOption = q.options?.[correctIndex];

      if (selected && selected === correctOption) {
        correct += 1;
      }
    });

    setScore(correct);
    setSubmitted(true);
  };

  return (
    <div style={{ padding: 24, fontFamily: "Arial", maxWidth: 900, margin: "0 auto" }}>
      <h1>SecureAI CBT Paper</h1>

      <form onSubmit={handleGenerate} style={{ marginBottom: 24 }}>
        <select
          value={selectedExam}
          onChange={(e) => setSelectedExam(e.target.value)}
          style={{ padding: 8, marginRight: 12 }}
        >
          <option value="NEET">NEET</option>
          <option value="JEE">JEE</option>
        </select>

        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Paper"}
        </button>
      </form>

      {error && <div style={{ color: "red", marginBottom: 16 }}>{error}</div>}

      {paper?.questions?.length ? (
        <div>
          <h2>{paper.paper_id || "Generated Paper"}</h2>
          <p>Exam ID: {paper.exam_id}</p>

          <form onSubmit={handleSubmitPaper}>
            {paper.questions.map((q, index) => (
              <div
                key={`${q.question_no}-${index}`}
                style={{
                  border: "1px solid #ccc",
                  padding: 16,
                  marginBottom: 16,
                  borderRadius: 8,
                  background: submitted && q.answer
                    ? (answers[`${q.question_no}-${index}`] === q.options?.[{ a: 0, b: 1, c: 2, d: 3 }[String(q.answer).toLowerCase()]]
                      ? "#e8ffe8"
                      : "#ffe8e8")
                    : "white",
                }}
              >
                <p>
                  <strong>{index + 1}.</strong> <strong>[{q.subject}]</strong> {q.question}
                </p>

                <p style={{ fontSize: 14, color: "#666" }}>
                  Question No: {q.question_no} | Page: {q.page}
                </p>

                {q.options?.map((opt, idx) => (
                  <label key={idx} style={{ display: "block", marginBottom: 6 }}>
                    <input
                      type="radio"
                      name={`q-${q.question_no}-${index}`}
                      value={opt}
                      checked={answers[`${q.question_no}-${index}`] === opt}
                      onChange={() => handleAnswerChange(`${q.question_no}-${index}`, opt)}
                      disabled={submitted}
                    />{" "}
                    {opt}
                  </label>
                ))}
              </div>
            ))}

            <button type="submit" disabled={submitted} style={{ padding: "10px 18px" }}>
              Submit Paper
            </button>
          </form>

          {submitted && score !== null && (
            <div style={{ marginTop: 24, padding: 16, background: "#f4f4f4", borderRadius: 8 }}>
              <h3>Result</h3>
              <p>Score: {score} / {paper.questions.length}</p>
            </div>
          )}
        </div>
      ) : (
        !loading && !error && <div>No paper loaded yet.</div>
      )}
    </div>
  );
}
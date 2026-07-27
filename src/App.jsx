import { useState, useEffect, useRef, useCallback } from "react";
import "./App.css";

// ---- constants -------------------------------------------------------

const SECTIONS = ["Physics", "Chemistry", "Mathematics"];
const EXAM_DURATION_SECONDS = 3 * 60 * 60; // 3 hours, like the real JEE CBT

const STATUS = {
  NOT_VISITED: "not-visited",
  NOT_ANSWERED: "not-answered",
  ANSWERED: "answered",
  MARKED: "marked",
  ANSWERED_MARKED: "answered-marked",
};

const OPTION_LETTERS = ["A", "B", "C", "D"];
const ANSWER_INDEX = { a: 0, b: 1, c: 2, d: 3 };

function formatTime(totalSeconds) {
  const h = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
  const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const s = String(totalSeconds % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

function correctOptionText(q) {
  const idx = ANSWER_INDEX[String(q.answer).toLowerCase()];
  return q.options?.[idx];
}

// ---- main component ---------------------------------------------------

export default function App() {
  // paper fetch state
  const [loading, setLoading] = useState(false);
  const [paper, setPaper] = useState(null);
  const [error, setError] = useState("");

  // exam-taking state
  const [started, setStarted] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [activeSection, setActiveSection] = useState(SECTIONS[0]);
  const [currentIndex, setCurrentIndex] = useState(0); // index within active section
  const [answers, setAnswers] = useState({}); // key -> selected option text
  const [statusMap, setStatusMap] = useState({}); // key -> STATUS
  const [secondsLeft, setSecondsLeft] = useState(EXAM_DURATION_SECONDS);
  const [confirmSubmit, setConfirmSubmit] = useState(false);
  const timerRef = useRef(null);

  // ---- fetch paper ----

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setPaper(null);

    try {
      const res = await fetch("/api/generate-paper", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
        },
        body: JSON.stringify({
          examType: "NEET",
          topic: "physics-chemistry-maths",
          difficulty: "medium",
          numQuestions: 30,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(JSON.stringify(data));
      } else {
        setPaper(data);
      }
    } catch (err) {
      setError(err.message || "Backend connection failed");
    } finally {
      setLoading(false);
    }
  };

  // group questions by subject, falling back to a single section if the
  // API doesn't return a `subject` field on every question
  const grouped = paper?.questions?.length
    ? SECTIONS.reduce((acc, sec) => {
      acc[sec] = paper.questions.filter(
        (q) => (q.subject || "").toLowerCase() === sec.toLowerCase()
      );
      return acc;
    }, {})
    : {};

  const hasAnyGrouped = Object.values(grouped).some((arr) => arr.length > 0);
  const effectiveGrouped = hasAnyGrouped
    ? grouped
    : { [SECTIONS[0]]: paper?.questions || [], [SECTIONS[1]]: [], [SECTIONS[2]]: [] };

  const activeQuestions = effectiveGrouped[activeSection] || [];
  const currentQuestion = activeQuestions[currentIndex];
  const currentKey = currentQuestion
    ? `${activeSection}-${currentQuestion.question_no}-${currentIndex}`
    : null;

  // ---- timer ----

  useEffect(() => {
    if (!started || submitted) return;
    timerRef.current = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(timerRef.current);
          setSubmitted(true);
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [started, submitted]);

  // mark question as visited when it becomes current
  useEffect(() => {
    if (!currentKey) return;
    setStatusMap((prev) => {
      if (prev[currentKey]) return prev;
      return { ...prev, [currentKey]: STATUS.NOT_ANSWERED };
    });
  }, [currentKey]);

  const setKeyStatus = useCallback((key, status) => {
    setStatusMap((prev) => ({ ...prev, [key]: status }));
  }, []);

  // ---- actions ----

  const handleStart = () => {
    setStarted(true);
    setCurrentIndex(0);
    setActiveSection(SECTIONS.find((s) => effectiveGrouped[s]?.length) || SECTIONS[0]);
  };

  const selectOption = (option) => {
    if (!currentKey) return;
    setAnswers((prev) => ({ ...prev, [currentKey]: option }));
  };

  const goTo = (section, index) => {
    setActiveSection(section);
    setCurrentIndex(index);
  };

  const saveAndNext = () => {
    if (currentKey) {
      const hasAnswer = !!answers[currentKey];
      const wasMarked =
        statusMap[currentKey] === STATUS.MARKED ||
        statusMap[currentKey] === STATUS.ANSWERED_MARKED;
      setKeyStatus(
        currentKey,
        hasAnswer
          ? wasMarked
            ? STATUS.ANSWERED_MARKED
            : STATUS.ANSWERED
          : STATUS.NOT_ANSWERED
      );
    }
    stepForward();
  };

  const markForReview = () => {
    if (currentKey) {
      const hasAnswer = !!answers[currentKey];
      setKeyStatus(currentKey, hasAnswer ? STATUS.ANSWERED_MARKED : STATUS.MARKED);
    }
    stepForward();
  };

  const clearResponse = () => {
    if (!currentKey) return;
    setAnswers((prev) => {
      const next = { ...prev };
      delete next[currentKey];
      return next;
    });
    setKeyStatus(currentKey, STATUS.NOT_ANSWERED);
  };

  const stepForward = () => {
    if (currentIndex < activeQuestions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      const nextSectionIdx = SECTIONS.indexOf(activeSection) + 1;
      if (nextSectionIdx < SECTIONS.length) {
        setActiveSection(SECTIONS[nextSectionIdx]);
        setCurrentIndex(0);
      }
    }
  };

  const doSubmit = () => {
    setConfirmSubmit(false);
    setSubmitted(true);
  };

  // ---- scoring (NEET-style +4 / -1) ----

  const scoreSummary = (() => {
    if (!paper?.questions?.length) return null;
    let correct = 0,
      incorrect = 0,
      unattempted = 0;

    SECTIONS.forEach((sec) => {
      (effectiveGrouped[sec] || []).forEach((q, idx) => {
        const key = `${sec}-${q.question_no}-${idx}`;
        const selected = answers[key];
        if (!selected) {
          unattempted += 1;
        } else if (selected === correctOptionText(q)) {
          correct += 1;
        } else {
          incorrect += 1;
        }
      });
    });

    const marks = correct * 4 - incorrect * 1;
    const total = correct + incorrect + unattempted;
    return { correct, incorrect, unattempted, marks, total };
  })();

  // ---- render: fetch screen ----

  if (!paper) {
    return (
      <div className="app-container">
        <div className="card">
          <h1 className="title">NEET CBT Mock</h1>
          <p className="subtle-text">
            Physics · Chemistry · Mathematics — full-length computer based test.
          </p>
          <button className="generate-btn" onClick={handleGenerate} disabled={loading}>
            {loading ? "Generating paper..." : "Generate NEET Paper"}
          </button>
          {error && <div className="error-box">{error}</div>}
        </div>
      </div>
    );
  }

  // ---- render: instructions / start screen ----

  if (paper && !started && !submitted) {
    return (
      <div className="app-container">
        <div className="card">
          <h1 className="title">{paper.paper_id || "NEET Mock Paper"}</h1>
          <p className="subtle-text">Exam ID: {paper.exam_id}</p>
          <ul className="instructions-list">
            <li>Duration: 3 hours. The test auto-submits when time runs out.</li>
            <li>Each correct answer: +4 marks. Each incorrect answer: −1 mark.</li>
            <li>Use "Save & Next" to record a response and move on.</li>
            <li>Use "Mark for Review & Next" to flag a question to revisit.</li>
            <li>Navigate freely across Physics, Chemistry, and Mathematics.</li>
          </ul>
          <div style={{ textAlign: "center" }}>
            <button className="main-btn" onClick={handleStart}>
              Start Test
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---- render: result screen ----

  if (submitted) {
    return (
      <div className="app-container">
        <div className="card">
          <h1 className="title">Test Submitted</h1>
          <div className="result-grid">
            <div className="result-cell">
              <div className="result-num correct">{scoreSummary.correct}</div>
              <div className="result-label">Correct</div>
            </div>
            <div className="result-cell">
              <div className="result-num incorrect">{scoreSummary.incorrect}</div>
              <div className="result-label">Incorrect</div>
            </div>
            <div className="result-cell">
              <div className="result-num unattempted">{scoreSummary.unattempted}</div>
              <div className="result-label">Unattempted</div>
            </div>
          </div>
          <div className="marks-banner">
            Total marks: {scoreSummary.marks} / {scoreSummary.total * 4}
          </div>
        </div>
      </div>
    );
  }

  // ---- render: main exam interface ----

  return (
    <div className="exam-shell">
      <div className="top-bar">
        <div className="top-bar-title">{paper.paper_id || "JEE Mock Paper"}</div>
        <div className="timer">
          Time Left: <strong>{formatTime(secondsLeft)}</strong>
        </div>
      </div>

      <div className="section-tabs">
        {SECTIONS.map((sec) => (
          <button
            key={sec}
            onClick={() => goTo(sec, 0)}
            className={`section-tab ${sec === activeSection ? "active" : ""}`}
          >
            {sec}
          </button>
        ))}
      </div>

      <div className="exam-body">
        <div className="question-panel">
          {currentQuestion ? (
            <>
              <div className="question-meta">
                Question {currentIndex + 1} of {activeQuestions.length} · {activeSection}
              </div>
              <p className="question-text">{currentQuestion.question}</p>

              <div className="options-list">
                {currentQuestion.options?.map((opt, idx) => (
                  <label
                    key={idx}
                    className={`option-row ${answers[currentKey] === opt ? "selected" : ""}`}
                  >
                    <input
                      type="radio"
                      name={currentKey}
                      checked={answers[currentKey] === opt}
                      onChange={() => selectOption(opt)}
                      style={{ marginRight: 10 }}
                    />
                    <span className="option-letter">{OPTION_LETTERS[idx]}.</span> {opt}
                  </label>
                ))}
              </div>

              <div className="action-row">
                <button className="ghost-btn" onClick={clearResponse}>
                  Clear Response
                </button>
                <button className="mark-btn" onClick={markForReview}>
                  Mark for Review & Next
                </button>
                <button className="main-btn" onClick={saveAndNext}>
                  Save & Next
                </button>
              </div>
            </>
          ) : (
            <p className="subtle-text">No questions in this section.</p>
          )}
        </div>

        <div className="palette-panel">
          <div className="legend">
            <div className="legend-item">
              <span className="legend-dot answered" /> Answered
            </div>
            <div className="legend-item">
              <span className="legend-dot not-answered" /> Not Answered
            </div>
            <div className="legend-item">
              <span className="legend-dot not-visited" /> Not Visited
            </div>
            <div className="legend-item">
              <span className="legend-dot marked" /> Marked
            </div>
          </div>

          <div className="palette-grid">
            {activeQuestions.map((q, idx) => {
              const key = `${activeSection}-${q.question_no}-${idx}`;
              const st = statusMap[key] || STATUS.NOT_VISITED;
              return (
                <button
                  key={key}
                  onClick={() => goTo(activeSection, idx)}
                  className={`palette-cell ${st} ${idx === currentIndex ? "current" : ""}`}
                >
                  {idx + 1}
                </button>
              );
            })}
          </div>

          <button className="submit-btn" onClick={() => setConfirmSubmit(true)}>
            Submit Test
          </button>
        </div>
      </div>

      {confirmSubmit && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h3 style={{ marginTop: 0 }}>Submit the test?</h3>
            <p className="subtle-text">
              You won't be able to change your answers after submitting.
            </p>
            <div className="action-row">
              <button className="ghost-btn" onClick={() => setConfirmSubmit(false)}>
                Cancel
              </button>
              <button className="main-btn" onClick={doSubmit}>
                Yes, Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

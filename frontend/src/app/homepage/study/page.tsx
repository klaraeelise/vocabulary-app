"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken, isTokenExpired, logout } from "@/lib/auth";

interface Meaning {
  id: number;
  definition: string;
  note?: string;
  language_name: string;
}

interface Word {
  progress_id: number;
  word_id: number;
  word: string;
  status: string;
  wordtype_name: string;
  language_name: string;
  meanings: Meaning[];
}

export default function StudyPage() {
  const router = useRouter();
  const [words, setWords] = useState<Word[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sessionStats, setSessionStats] = useState({ correct: 0, total: 0 });

  useEffect(() => {
    fetchDueWords();
  }, []);

  const fetchDueWords = async () => {
    const token = getAuthToken();
    
    if (!token || isTokenExpired()) {
      logout();
      router.push("/auth/login");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/review/due?limit=20", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        if (res.status === 401) {
          logout();
          router.push("/auth/login");
          return;
        }
        throw new Error("Failed to fetch words");
      }

      const data = await res.json();
      setWords(data.words);
      
      if (data.words.length === 0) {
        setError("No words due for review! Great job! 🎉");
      }
    } catch (err) {
      setError("Failed to load words. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (correct: boolean, difficulty: string) => {
    const token = getAuthToken();
    const currentWord = words[currentIndex];

    try {
      const res = await fetch("http://127.0.0.1:8000/review/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          word_id: currentWord.word_id,
          correct,
          difficulty,
        }),
      });

      if (!res.ok) throw new Error("Failed to submit review");

      // Update session stats
      setSessionStats({
        correct: sessionStats.correct + (correct ? 1 : 0),
        total: sessionStats.total + 1,
      });

      // Move to next word
      if (currentIndex < words.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setShowAnswer(false);
      } else {
        // Session complete
        alert(`Session complete! ${sessionStats.correct + (correct ? 1 : 0)}/${sessionStats.total + 1} correct`);
        router.push("/homepage");
      }
    } catch (err) {
      alert("Failed to submit answer. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-ci_linen">
        <div className="text-xl text-ci_black">Loading your words...</div>
      </div>
    );
  }

  if (error || words.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-ci_linen text-ci_black">
        <h1 className="text-3xl font-bold mb-4">{error || "No words to review"}</h1>
        <button
          onClick={() => router.push("/homepage")}
          className="px-6 py-3 bg-ci_turquoise hover:bg-ci_turquoise/80 rounded-lg"
        >
          Back to Home
        </button>
      </div>
    );
  }

  const currentWord = words[currentIndex];
  const progress = ((currentIndex + 1) / words.length) * 100;

  return (
    <div className="min-h-screen bg-ci_linen p-6">
      {/* Header with progress */}
      <div className="max-w-2xl mx-auto mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-ci_black font-medium">
            Word {currentIndex + 1} of {words.length}
          </span>
          <span className="text-ci_black">
            Session: {sessionStats.correct}/{sessionStats.total}
          </span>
        </div>
        <div className="w-full bg-gray-300 rounded-full h-2">
          <div
            className="bg-ci_turquoise h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Flashcard */}
      <div className="max-w-2xl mx-auto">
        <div
          className={`bg-white rounded-2xl shadow-lg p-8 min-h-[400px] cursor-pointer transition-transform hover:scale-105 ${
            showAnswer ? "bg-ci_yellow/20" : ""
          }`}
          onClick={() => !showAnswer && setShowAnswer(true)}
        >
          {/* Front side - Word */}
          <div className="text-center">
            <h2 className="text-4xl font-bold text-ci_black mb-4">
              {currentWord.word}
            </h2>
            <p className="text-lg text-ci_brown mb-6">
              {currentWord.wordtype_name} • {currentWord.language_name}
            </p>
            
            {!showAnswer && (
              <p className="text-gray-500 italic mt-12">
                Click to reveal answer
              </p>
            )}
          </div>

          {/* Back side - Meanings */}
          {showAnswer && (
            <div className="mt-8 space-y-4">
              <h3 className="text-xl font-semibold text-ci_black border-t pt-4">
                Meanings:
              </h3>
              {currentWord.meanings.map((meaning, idx) => (
                <div key={idx} className="border-l-4 border-ci_turquoise pl-4">
                  <p className="text-lg text-ci_black">{meaning.definition}</p>
                  {meaning.note && (
                    <p className="text-sm text-gray-600 mt-1">
                      Note: {meaning.note}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    ({meaning.language_name})
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Answer buttons */}
        {showAnswer && (
          <div className="mt-6 space-y-4">
            <p className="text-center text-ci_black font-medium">
              How well did you remember?
            </p>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleAnswer(false, "hard")}
                className="px-6 py-4 bg-ci_red hover:bg-ci_red/80 text-white rounded-lg font-medium transition-colors"
              >
                ❌ Incorrect
              </button>
              <button
                onClick={() => handleAnswer(true, "hard")}
                className="px-6 py-4 bg-ci_yellow hover:bg-ci_yellow/80 text-ci_black rounded-lg font-medium transition-colors"
              >
                😅 Hard
              </button>
              <button
                onClick={() => handleAnswer(true, "medium")}
                className="px-6 py-4 bg-ci_rose hover:bg-ci_rose/80 text-ci_black rounded-lg font-medium transition-colors"
              >
                🙂 Medium
              </button>
              <button
                onClick={() => handleAnswer(true, "easy")}
                className="px-6 py-4 bg-ci_turquoise hover:bg-ci_turquoise/80 text-white rounded-lg font-medium transition-colors"
              >
                ✅ Easy
              </button>
            </div>
          </div>
        )}

        {/* Keyboard hint */}
        {!showAnswer && (
          <p className="text-center text-gray-500 mt-4 text-sm">
            Press Space to flip card
          </p>
        )}
      </div>
    </div>
  );
}
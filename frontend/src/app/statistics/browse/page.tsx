"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken, isTokenExpired, logout } from "@/lib/auth";

interface Subject {
  id: number;
  name: string;
  code: string;
  description: string;
  question_count: number;
}

interface Question {
  id: number;
  question_text: string;
  question_latex?: string;
  difficulty_level: string;
  question_type: string;
  options: Array<{
    id: number;
    option_text: string;
    option_latex?: string;
  }>;
}

export default function BrowseStatisticsPage() {
  const router = useRouter();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [difficulty, setDifficulty] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    checkAuthAndFetchSubjects();
  }, []);

  const checkAuthAndFetchSubjects = async () => {
    const token = getAuthToken();
    
    if (!token || isTokenExpired()) {
      logout();
      router.push("/auth/login");
      return;
    }

    fetchSubjects();
  };

  const fetchSubjects = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/subjects/");
      if (!res.ok) throw new Error("Failed to fetch subjects");
      
      const data = await res.json();
      setSubjects(data.subjects);
      
      // Auto-select Statistics subject
      const statsSubject = data.subjects.find((s: Subject) => s.code === "STAT");
      if (statsSubject) {
        setSelectedSubject(statsSubject);
        fetchQuestions(statsSubject.id);
      }
    } catch (err) {
      setError("Failed to load subjects");
    } finally {
      setLoading(false);
    }
  };

  const fetchQuestions = async (subjectId: number, diff?: string) => {
    setLoading(true);
    try {
      let url = `http://127.0.0.1:8000/subjects/${subjectId}/questions?limit=20`;
      if (diff && diff !== "all") {
        url += `&difficulty=${diff}`;
      }
      
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch questions");
      
      const data = await res.json();
      setQuestions(data.questions);
    } catch (err) {
      setError("Failed to load questions");
    } finally {
      setLoading(false);
    }
  };

  const handleDifficultyChange = (newDiff: string) => {
    setDifficulty(newDiff);
    if (selectedSubject) {
      fetchQuestions(selectedSubject.id, newDiff);
    }
  };

  const handleAddToLearning = async (questionId: number) => {
    const token = getAuthToken();
    
    try {
      const res = await fetch("http://127.0.0.1:8000/question-review/add-question", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question_id: questionId }),
      });

      if (!res.ok) {
        const data = await res.json();
        if (data.detail?.includes("already in learning queue")) {
          alert("This question is already in your learning queue!");
        } else {
          throw new Error("Failed to add question");
        }
        return;
      }

      alert("Question added to your learning queue! ✅");
      
      // Refresh questions to show updated state
      if (selectedSubject) {
        fetchQuestions(selectedSubject.id, difficulty);
      }
    } catch (err) {
      alert("Failed to add question. Please try again.");
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case "beginner": return "bg-green-100 text-green-800";
      case "intermediate": return "bg-yellow-100 text-yellow-800";
      case "advanced": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  if (loading && !selectedSubject) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-ci_linen">
        <div className="text-xl text-ci_black">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-ci_linen p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="mb-4 text-ci_brown hover:text-ci_black"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-ci_black mb-2">Browse Statistics Topics</h1>
          <p className="text-ci_brown">Explore and add questions to your learning queue</p>
        </div>

        {/* Subject Info */}
        {selectedSubject && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-2xl font-bold text-ci_black mb-2">{selectedSubject.name}</h2>
            <p className="text-ci_brown mb-4">{selectedSubject.description}</p>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                📊 {selectedSubject.question_count} questions available
              </span>
            </div>
          </div>
        )}

        {/* Difficulty Filter */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <label className="block text-sm font-medium text-ci_black mb-2">
            Filter by Difficulty:
          </label>
          <div className="flex gap-2">
            {["all", "beginner", "intermediate", "advanced"].map((diff) => (
              <button
                key={diff}
                onClick={() => handleDifficultyChange(diff)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  difficulty === diff
                    ? "bg-ci_turquoise text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {diff.charAt(0).toUpperCase() + diff.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Questions List */}
        {error && (
          <div className="bg-red-100 text-red-800 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center text-ci_black">Loading questions...</div>
        ) : questions.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-ci_brown">No questions found for this difficulty level.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {questions.map((question) => (
              <div key={question.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium mb-2 ${getDifficultyColor(question.difficulty_level)}`}>
                      {question.difficulty_level}
                    </span>
                    <h3 className="text-lg font-semibold text-ci_black mb-2">
                      {question.question_text}
                    </h3>
                    {question.question_latex && (
                      <div className="text-sm text-gray-600 font-mono bg-gray-50 p-2 rounded mb-2">
                        {question.question_latex}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handleAddToLearning(question.id)}
                    className="ml-4 px-4 py-2 bg-ci_turquoise hover:bg-ci_turquoise/80 text-white rounded-lg font-medium transition-colors"
                  >
                    + Add to Queue
                  </button>
                </div>

                {/* Answer Options Preview */}
                <div className="mt-4">
                  <p className="text-sm text-gray-600 mb-2">Answer options:</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {question.options.slice(0, 4).map((option, idx) => (
                      <div key={option.id} className="bg-gray-50 p-3 rounded border border-gray-200">
                        <span className="font-medium text-ci_black">
                          {String.fromCharCode(65 + idx)}. 
                        </span>{" "}
                        <span className="text-ci_brown">{option.option_text}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
                  <span>Type: {question.question_type}</span>
                  <span>ID: #{question.id}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-8 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg shadow-md p-6 text-center">
          <h3 className="text-xl font-bold text-ci_black mb-2">Ready to Start Learning?</h3>
          <p className="text-ci_brown mb-4">
            Add questions to your queue and start studying with spaced repetition!
          </p>
          <button
            onClick={() => router.push("/statistics/study")}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white rounded-lg font-medium transition-all"
          >
            Go to Study Mode →
          </button>
        </div>
      </div>
    </div>
  );
}

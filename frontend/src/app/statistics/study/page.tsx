"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken, isTokenExpired, logout } from "@/lib/auth";
import { getDueQuestions, submitQuestionReview } from "@/lib/api";

interface Option {
  id: number;
  option_text: string;
  option_latex?: string;
}

interface Question {
  progress_id: number;
  question_id: number;
  question_text: string;
  question_latex?: string;
  difficulty_level: string;
  status: string;
  subject_name: string;
  question_type: string;
  options: Option[];
}

export default function StudyStatisticsPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sessionStats, setSessionStats] = useState({ correct: 0, total: 0 });

  useEffect(() => {
    fetchDueQuestionsData();
  }, []);

  const fetchDueQuestionsData = async () => {
    const token = getAuthToken();
    
    if (!token || isTokenExpired()) {
      logout();
      router.push("/auth/login");
      return;
    }

    try {
      const data = await getDueQuestions(undefined, 20);
      setQuestions(data.questions);
      
      if (data.questions.length === 0) {
        setError("No questions due for review! Great job! 🎉\nAdd more questions from the Browse page.");
      }
    } catch (err) {
      setError("Failed to load questions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (selectedOption === null) {
      alert("Please select an answer!");
      return;
    }

    const currentQuestion = questions[currentIndex];

    try {
      const data = await submitQuestionReview(currentQuestion.question_id, selectedOption);
      setResult(data);
      setShowResult(true);

      // Update session stats
      setSessionStats({
        correct: sessionStats.correct + (data.correct ? 1 : 0),
        total: sessionStats.total + 1,
      });
    } catch (err) {
      alert("Failed to submit answer. Please try again.");
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedOption(null);
      setShowResult(false);
      setResult(null);
    } else {
      // Session complete
      alert(`Session complete! ${sessionStats.correct}/${sessionStats.total} correct`);
      router.push("/dashboard");
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-ci_linen">
        <div className="text-xl text-ci_black">Loading your questions...</div>
      </div>
    );
  }

  if (error || questions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-ci_linen text-ci_black p-6">
        <h1 className="text-3xl font-bold mb-4 text-center">{error || "No questions to review"}</h1>
        <div className="space-x-4">
          <button
            onClick={() => router.push("/statistics/browse")}
            className="px-6 py-3 bg-ci_turquoise hover:bg-ci_turquoise/80 text-white rounded-lg"
          >
            Browse Questions
          </button>
          <button
            onClick={() => router.push("/dashboard")}
            className="px-6 py-3 bg-gray-300 hover:bg-gray-400 text-ci_black rounded-lg"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-ci_linen p-6">
      {/* Header with progress */}
      <div className="max-w-3xl mx-auto mb-6">
        <button
          onClick={() => router.push("/dashboard")}
          className="mb-4 text-ci_brown hover:text-ci_black"
        >
          ← Back to Dashboard
        </button>
        <div className="flex justify-between items-center mb-2">
          <span className="text-ci_black font-medium">
            Question {currentIndex + 1} of {questions.length}
          </span>
          <span className="text-ci_black">
            Session: {sessionStats.correct}/{sessionStats.total} correct
          </span>
        </div>
        <div className="w-full bg-gray-300 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-purple-500 to-indigo-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Question Card */}
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          {/* Question Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(currentQuestion.difficulty_level)}`}>
                {currentQuestion.difficulty_level}
              </span>
              <span className="text-xs text-gray-500">
                {currentQuestion.subject_name} • {currentQuestion.question_type}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-ci_black mb-3">
              {currentQuestion.question_text}
            </h2>
            {currentQuestion.question_latex && (
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-900 font-mono">
                  {currentQuestion.question_latex}
                </p>
              </div>
            )}
          </div>

          {/* Answer Options */}
          <div className="space-y-3">
            {currentQuestion.options.map((option, idx) => {
              const isSelected = selectedOption === option.id;
              const isCorrect = result && result.correct_answer_id === option.id;
              const isWrong = showResult && isSelected && !result.correct;
              
              let optionClass = "border-2 p-4 rounded-lg cursor-pointer transition-all ";
              if (showResult) {
                if (isCorrect) {
                  optionClass += "border-green-500 bg-green-50";
                } else if (isWrong) {
                  optionClass += "border-red-500 bg-red-50";
                } else {
                  optionClass += "border-gray-200 bg-gray-50 cursor-not-allowed";
                }
              } else {
                optionClass += isSelected
                  ? "border-purple-500 bg-purple-50"
                  : "border-gray-200 hover:border-purple-300 hover:bg-purple-50/50";
              }

              return (
                <div
                  key={option.id}
                  onClick={() => !showResult && setSelectedOption(option.id)}
                  className={optionClass}
                >
                  <div className="flex items-start">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-ci_brown/10 flex items-center justify-center mr-3">
                      <span className="font-semibold text-ci_brown">
                        {String.fromCharCode(65 + idx)}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="text-ci_black">{option.option_text}</p>
                      {option.option_latex && (
                        <p className="text-sm text-gray-600 font-mono mt-1">
                          {option.option_latex}
                        </p>
                      )}
                    </div>
                    {showResult && isCorrect && (
                      <span className="ml-2 text-green-600 font-bold">✓</span>
                    )}
                    {showResult && isWrong && (
                      <span className="ml-2 text-red-600 font-bold">✗</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Result Feedback */}
          {showResult && result && (
            <div className={`mt-6 p-6 rounded-lg ${result.correct ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'}`}>
              <div className="flex items-start gap-3">
                <div className={`text-3xl ${result.correct ? 'text-green-600' : 'text-red-600'}`}>
                  {result.correct ? '✓' : '✗'}
                </div>
                <div className="flex-1">
                  <h3 className={`text-xl font-bold mb-2 ${result.correct ? 'text-green-900' : 'text-red-900'}`}>
                    {result.correct ? 'Correct!' : 'Incorrect'}
                  </h3>
                  {!result.correct && result.correct_answer && (
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>Correct answer:</strong> {result.correct_answer}
                    </p>
                  )}
                  {result.question_explanation && (
                    <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                      <p className="text-sm text-gray-800">
                        <strong>Explanation:</strong> {result.question_explanation}
                      </p>
                    </div>
                  )}
                  <div className="mt-3 text-sm text-gray-600">
                    <p>Next review: in {result.interval_days} day{result.interval_days !== 1 ? 's' : ''}</p>
                    <p>Status: <span className="font-medium">{result.status}</span></p>
                    <p>Your accuracy: <span className="font-medium">{result.accuracy}%</span></p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Button */}
          <div className="mt-6">
            {!showResult ? (
              <button
                onClick={handleSubmit}
                disabled={selectedOption === null}
                className={`w-full px-6 py-4 rounded-lg font-medium text-white transition-all ${
                  selectedOption === null
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600'
                }`}
              >
                Submit Answer
              </button>
            ) : (
              <button
                onClick={handleNext}
                className="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white rounded-lg font-medium transition-all"
              >
                {currentIndex < questions.length - 1 ? 'Next Question →' : 'Complete Session'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

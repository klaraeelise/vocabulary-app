// app/dashboard/page.tsx

import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-ci_linen text-ci_black">
      {/* Header */}
      <section className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-wide">Welcome Back</h1>
        <p className="text-lg text-ci_brown opacity-80">
          What would you like to do today?
        </p>
      </section>

      {/* Navigation Buttons */}
      <nav className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-12 w-full max-w-2xl px-4">
        {/* Language Learning Section */}
        <div className="col-span-full">
          <h2 className="text-2xl font-semibold mb-4 text-ci_brown">Language Learning</h2>
        </div>
        
        {/* Add Word */}
        <Link href="/add-word">
          <button className="w-full px-6 py-4 rounded-2xl bg-ci_yellow hover:bg-ci_yellow/80 text-ci_black font-medium shadow-md transition-all duration-300">
            ➕ Add Flashcard
          </button>
        </Link>

        {/* Fetch Words */}
        <Link href="/fetch">
          <button className="w-full px-6 py-4 rounded-2xl bg-ci_turquoise hover:bg-ci_turquoise/80 text-ci_linen font-medium shadow-md transition-all duration-300">
            🌐 Fetch Vocabulary
          </button>
        </Link>

        {/* Study Vocabulary */}
        <Link href="/study">
          <button className="w-full px-6 py-4 rounded-2xl bg-ci_rose hover:bg-ci_rose/80 text-ci_black font-medium shadow-md transition-all duration-300">
            📚 Study Vocabulary
          </button>
        </Link>

        {/* Statistics Learning Section */}
        <div className="col-span-full mt-8">
          <h2 className="text-2xl font-semibold mb-4 text-ci_brown">Statistics Learning</h2>
        </div>

        {/* Browse Statistics Topics */}
        <Link href="/statistics/browse">
          <button className="w-full px-6 py-4 rounded-2xl bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white font-medium shadow-md transition-all duration-300">
            📊 Browse Topics
          </button>
        </Link>

        {/* Study Statistics */}
        <Link href="/statistics/study">
          <button className="w-full px-6 py-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-medium shadow-md transition-all duration-300">
            🧮 Study Statistics
          </button>
        </Link>
      </nav>
    </main>
  );
}

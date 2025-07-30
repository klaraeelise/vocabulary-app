// src/app/homepage/page.tsx

import Link from "next/link";

export default function Homepage() {
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
      <nav className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-12 w-full max-w-lg">
        {/* Add Word */}
        <Link href="/homepage/add-word">
          <button className="w-full px-6 py-4 rounded-2xl bg-ci_yellow hover:bg-ci_yellow/80 text-ci_black font-medium shadow-md transition-all duration-300">
            ➕ Add Flashcard
          </button>
        </Link>

        {/* Fetch Words */}
        <Link href="/homepage/fetch">
          <button className="w-full px-6 py-4 rounded-2xl bg-ci_turquoise hover:bg-ci_turquoise/80 text-ci_linen font-medium shadow-md transition-all duration-300">
            🌐 Fetch Vocabulary
          </button>
        </Link>

        {/* Study */}
        <Link href="/homepage/study">
          <button className="w-full px-6 py-4 rounded-2xl bg-ci_rose hover:bg-ci_rose/80 text-ci_black font-medium shadow-md transition-all duration-300">
            📚 Study
          </button>
        </Link>

        {/* Dashboard */}
        <Link href="@/dashboard">
          <button className="w-full px-6 py-4 rounded-2xl bg-ci_red hover:bg-ci_red/80 text-ci_linen font-medium shadow-md transition-all duration-300">
            📊 Dashboard
          </button>
        </Link>
      </nav>
    </main>
  );
}

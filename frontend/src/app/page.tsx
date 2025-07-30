// app/page.tsx
"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/homepage"); // Auto-redirect if logged in
    }
  }, [router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-ci_linen text-ci_turquoise p-6">
      <h1 className="text-5xl font-bold mb-4">Welcome to VocabApp</h1>
      <p className="mb-8 text-lg text-ci_black/80">
        Build your vocabulary with spaced repetition and smart study tools.
      </p>
      <button
        onClick={() => router.push("/auth/login")}
        className="rounded-xl bg-white px-6 py-3 text-ci_turquoise font-semibold shadow-md hover:scale-105 transform transition"
      >
        Get Started
      </button>
      <button
  type="button"
  onClick={() => router.push("/auth/register")}
  className="rounded bg-foam text-abyss py-2 font-semibold"
>
  Register
</button>

    </div>
  );
}

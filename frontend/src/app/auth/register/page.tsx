"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Registration failed");
        return;
      }

      setSuccess("Registration successful! You can now log in.");
      setTimeout(() => router.push("/auth/login"), 1500);
    } catch (err) {
      setError("Server error. Please try again.");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-abyss text-foam">
      <div className="w-full max-w-sm rounded-2xl bg-kelp p-6 shadow-lg">
        <h1 className="mb-6 text-2xl font-bold text-center">Register</h1>
        <form onSubmit={handleRegister} className="flex flex-col space-y-4">
          <input
            type="email"
            placeholder="Email"
            className="rounded p-2 bg-foam text-abyss"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            className="rounded p-2 bg-foam text-abyss"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="text-red-400 text-sm">{error}</p>}
          {success && <p className="text-green-400 text-sm">{success}</p>}
          <button type="submit" className="rounded bg-glow py-2 text-abyss font-semibold">
            Register
          </button>
        </form>
      </div>
    </div>
  );
}

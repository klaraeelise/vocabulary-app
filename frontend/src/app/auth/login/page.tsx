// app/auth/login/page.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { saveAuthToken, setupAutoLogout } from "@/lib/auth";

export default function LoginPage() {
  //Setting up state variables for email, password, and error message, especially setting them to empty state so they can take user input
  const [error, setError] = useState(""); 
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  //Using Next.js router to handle navigation
  //This allows to redirect the user after successful login
  const router = useRouter();
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://vocabulary-app-python-service:8000";

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault(); //prevents reload of the page on form submission but rather handle everything in react
    setError(""); // reset error

    try {
      // Send login request to backend, using fetch to send a POST request to the backend login endpoint
      // The body contains the email and password in JSON format
      // The backend should return a token if login is successful
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      console.log("Response status:", res.status);
      console.log("Response data:", data);

      if (!res.ok) {
        setError(data.detail || "Login failed. Check email/password.");
        return;
      }

      // Save token with expiry time
      saveAuthToken(data.token, data.expires_at);

      // Setup automatic logout after 24 hours
      setupAutoLogout(() => {
        alert("Your session has expired. Please log in again.");
        router.push("/auth/login");
      });

      // Redirect to homepage
      router.push("/homepage");
    } catch (err) {
      setError("Server error. Please try again.");
    }
  };

  return (
  <div className="flex h-screen items-center justify-center bg-ci_linen text-ci_black">
    <div className="w-full max-w-sm rounded-2xl bg-ci_turquoise p-6 shadow-lg">
      <h1 className="mb-6 text-2xl font-bold text-center">Login</h1>
      <form onSubmit={handleLogin} className="flex flex-col space-y-4">
        <input
          type="email"
          placeholder="Email"
          className="rounded p-2 bg-foam text-ci_black"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="rounded p-2 bg-foam text-ci_black"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button type="submit" className="rounded bg-glow py-2 text-ci_black font-semibold">
          Log in
        </button>
      </form>
    </div>
  </div>
);

}


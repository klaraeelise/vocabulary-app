// components/Navbar.tsx
"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { logout, isAuthenticated } from "@/lib/auth";

const navItems = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Study Today", path: "/study" },
  { name: "Fetch New Cards", path: "/fetch" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [loggedIn, setLoggedIn] = useState(false);

  // Check authentication state on mount and when pathname changes
  useEffect(() => {
    setLoggedIn(isAuthenticated());

    // Listen for custom auth state changes
    const handleAuthChange = () => {
      setLoggedIn(isAuthenticated());
    };

    // Listen for storage changes (across tabs/windows)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "token" || e.key === "token_expiry") {
        setLoggedIn(isAuthenticated());
      }
    };

    window.addEventListener("authStateChanged", handleAuthChange);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("authStateChanged", handleAuthChange);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [pathname]);

  const handleLogout = () => {
    logout(); // Clear token and expiry from localStorage
    setLoggedIn(false); // Update state immediately
    
    // Dispatch custom event for other components
    window.dispatchEvent(new Event("authStateChanged"));
    
    router.push("/auth/login");
  };

  return (
    <nav className="bg-ci_turquoise text-ci_black shadow-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between p-4">
        <h1 className="text-xl font-bold">VocabApp</h1>
        <ul className="flex space-x-6">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                href={item.path}
                className={`hover:text-white ${
                  pathname === item.path ? "font-semibold text-ci_black" : ""
                }`}
              >
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
        {loggedIn ? (
          <button
            onClick={handleLogout}
            className="rounded bg-kelp px-3 py-1 text-sm font-semibold hover:bg-ci_linen hover:text-ci_black"
          >
            Logout
          </button>
        ) : (
          <button
            onClick={() => router.push("/auth/login")}
            className="rounded bg-kelp px-3 py-1 text-sm font-semibold hover:bg-ci_linen hover:text-ci_black"
          >
            Login
          </button>
        )}
      </div>
    </nav>
  );
}

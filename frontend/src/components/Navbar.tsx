// components/Navbar.tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Study Today", path: "/dashboard/study" },
  { name: "Fetch New Cards", path: "/dashboard/fetch" },
];

export default function Navbar() {
  const pathname = usePathname();

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
        <button
          onClick={() => {
            localStorage.removeItem("token"); // Log out (simple)
            window.location.href = "/auth/login";
          }}
          className="rounded bg-kelp px-3 py-1 text-sm font-semibold hover:bg-ci_linen hover:text-ci_black"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

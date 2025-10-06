// src/app/homepage/page.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Homepage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboard
    router.replace("/dashboard");
  }, [router]);

  return null;
}

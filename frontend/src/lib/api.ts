// src/api.ts

// Fetch word data from scraper (via Next.js API route)
export async function fetchWord(word: string) {
  const res = await fetch(`/api/scrape?word=${encodeURIComponent(word)}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch word: ${res.statusText}`);
  }
  return res.json();
}

// Save word data to DB (via Python service proxy)
export async function saveWord(data: any) {
  const res = await fetch(`/api/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error(`Failed to save word: ${res.statusText}`);
  }
  return res.json();
}

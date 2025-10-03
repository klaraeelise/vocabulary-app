// src/api.ts

import { getAuthToken } from "./auth";

const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Make an authenticated API request
 */
async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = getAuthToken();
  
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  
  return fetch(url, {
    ...options,
    headers,
  });
}

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
  const res = await fetch(`${API_BASE_URL}/words/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || `Failed to save word: ${res.statusText}`);
  }
  return res.json();
}

// Fetch word from dictionary
export async function fetchWordFromDictionary(word: string, language: string) {
  const res = await fetch(
    `${API_BASE_URL}/fetch/word?word=${encodeURIComponent(word)}&language=${language}`
  );
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to fetch word from dictionary");
  }
  return res.json();
}

// Get supported languages for fetching
export async function getSupportedLanguages() {
  const res = await fetch(`${API_BASE_URL}/fetch/languages`);
  if (!res.ok) {
    throw new Error("Failed to get supported languages");
  }
  return res.json();
}

// Review endpoints
export async function getDueWords(limit: number = 20) {
  const res = await fetchWithAuth(
    `${API_BASE_URL}/review/due?limit=${limit}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch due words");
  }
  return res.json();
}

export async function submitReview(wordId: number, correct: boolean, difficulty: string) {
  const res = await fetchWithAuth(`${API_BASE_URL}/review/submit`, {
    method: "POST",
    body: JSON.stringify({
      word_id: wordId,
      correct,
      difficulty,
    }),
  });
  if (!res.ok) {
    throw new Error("Failed to submit review");
  }
  return res.json();
}

export async function getUserStats() {
  const res = await fetchWithAuth(`${API_BASE_URL}/review/stats`);
  if (!res.ok) {
    throw new Error("Failed to fetch user stats");
  }
  return res.json();
}

export async function addWordToLearning(wordId: number) {
  const res = await fetchWithAuth(`${API_BASE_URL}/review/add-word`, {
    method: "POST",
    body: JSON.stringify({ word_id: wordId }),
  });
  if (!res.ok) {
    throw new Error("Failed to add word to learning queue");
  }
  return res.json();
}

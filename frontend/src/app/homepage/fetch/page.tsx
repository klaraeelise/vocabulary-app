"use client";

import { useState } from "react";
import { fetchWord, saveWord } from "@/lib/api";
import SenseCard from "@/components/SenseCard";


type WordForm = {
  label: string;
  forms: string[];
  number?: string;
  definiteness?: string;
  gender?: string;
  degree?: string;
  tense?: string;
};

type Sense = {
  id: string;
  category: string;
  gender?: string;
  article?: string;
  meanings: { description: string; examples?: string[] }[];
  expressions?: { phrase: string; explanation: string }[];
  word_forms?: WordForm[];
};

type WordEntry = {
  word: string;
  senses: Sense[];
};

export default function FetchPage() {
  const [word, setWord] = useState("");
  const [data, setData] = useState<WordEntry | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const handleFetch = async () => {
    if (!word.trim()) {
      setError("Please enter a word.");
      return;
    }
    setLoading(true);
    setError(null);
    setSaved(false);

    try {
      const result: WordEntry = await fetchWord(word);
      console.log("Fetched data:", result);
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!data) return;
    try {
      await saveWord(data);
      setSaved(true);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Fetch New Cards</h1>

      <div className="flex gap-2 mb-6">
        <input
          type="text"
          placeholder="Enter a word..."
          value={word}
          onChange={(e) => setWord(e.target.value)}
          className="flex-1 rounded border px-3 py-2 shadow-sm"
        />
        <button
          onClick={handleFetch}
          className="border rounded bg-ci_turquoise px-4 py-2 font-semibold text-ci_linen shadow"
          disabled={loading}
        >
          {loading ? "Fetching..." : "Fetch"}
        </button>
      </div>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      {data && (
        <div className="mt-6">
          <h2 className="text-3xl font-bold mb-4">{data.word}</h2>

          {data.senses.length > 0 ? (
            data.senses.map((sense) => <SenseCard key={sense.id} sense={sense} />)
          ) : (
            <p className="text-gray-500 mt-4">No senses found for this word.</p>
          )}

          <div className="mt-6 flex gap-3">
            <button
              onClick={handleSave}
              className="border rounded bg-green-600 px-4 py-2 font-semibold text-white shadow"
            >
              ✅ Confirm & Save
            </button>
            <button
              onClick={() => setData(null)}
              className="border rounded bg-gray-400 px-4 py-2 font-semibold text-white shadow"
            >
              ✏️ Edit / Fetch Again
            </button>
          </div>
          {saved && <p className="text-green-600 mt-3">✅ Word saved successfully!</p>}
        </div>
      )}
    </div>
  );
}


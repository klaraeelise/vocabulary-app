"use client";

import { useState } from "react";
import { fetchWord, saveWord } from "@/lib/api";

type Example = { sentence: string };
type Meaning = { description: string; examples?: Example[] };
type Expression = { phrase: string; explanation: string };
type WordForm = {
  label: string;
  forms: string[];
  number?: string;
  definiteness?: string;
  gender?: string;
  degree?: string;
  tense?: string;
};

export default function FetchPage() {
  const [word, setWord] = useState("");
  const [data, setData] = useState<null | {
    word: string;
    category: string;
    gender?: string;
    article?: string;
    meanings: Meaning[];
    expressions?: Expression[];
    word_forms?: WordForm[];
  }>(null);
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
      const result = await fetchWord(word);
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

      {/* Input Field */}
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

      {/* Error */}
      {error && <p className="text-red-600 mb-4">{error}</p>}

      {/* Preview */}
      {data && (
        <div className="mt-6 border rounded-lg shadow p-6 bg-white">
          {/* Word Header */}
          <h2 className="text-3xl font-bold mb-2">{data.word}</h2>
          <p className="text-gray-700 mb-4 text-lg">
            <span className="font-semibold">{data.category}</span>
            {data.gender && <> • {data.gender}</>}
            {data.article && <> • Article: {data.article}</>}
          </p>

          {/* Meanings */}
          <h3 className="text-xl font-semibold mt-6 mb-2">Meanings</h3>
          <ol className="list-decimal ml-5 space-y-3">
            {data.meanings.map((meaning, i) => (
              <li key={i} className="border rounded p-3 bg-gray-50 shadow-sm">
                <p className="font-medium text-gray-800">{meaning.description}</p>
                {meaning.examples && meaning.examples.length > 0 && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-blue-600 text-sm">
                      Show examples ({meaning.examples.length})
                    </summary>
                    <ul className="list-disc ml-6 mt-2 text-gray-700 text-sm">
                      {meaning.examples.map((ex, j) => (
                        <li key={j}>{ex.sentence}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </li>
            ))}
          </ol>

          {/* Word Forms (Bøyning) */}
          {data.word_forms && data.word_forms.length > 0 && (
            <div className="mt-8">
              <h3 className="text-xl font-semibold mb-2">Word Forms (Bøyning)</h3>
              <table className="w-full border-collapse rounded-lg overflow-hidden shadow">
                <thead>
                  <tr className="bg-gray-100 text-left">
                    <th className="p-2 font-semibold w-1/3">Label</th>
                    <th className="p-2 font-semibold w-1/3">Forms</th>
                    <th className="p-2 font-semibold w-1/3">Metadata</th>
                  </tr>
                </thead>
                <tbody>
                  {data.word_forms.map((form, i) => (
                    <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                      <td className="p-2 font-medium">{form.label}</td>
                      <td className="p-2">
                        {form.forms.map((f, idx) =>
                          ["å", "har"].includes(f) ? (
                            <span key={f + idx}>
                              {idx > 0 && "; "}
                              <em>{f}</em>
                            </span>
                          ) : (
                            <span key={f + idx}>
                              {idx > 0 && "; "}
                              {f}
                            </span>
                          )
                        )}
                      </td>
                      <td className="p-2 text-sm text-gray-600">
                        {[form.number && `Number: ${form.number}`,
                          form.gender && `Gender: ${form.gender}`,
                          form.definiteness && `Definiteness: ${form.definiteness}`,
                          form.degree && `Degree: ${form.degree}`,
                          form.tense && `Tense: ${form.tense}`]
                          .filter(Boolean)
                          .join(" • ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Expressions */}
          {data.expressions && data.expressions.length > 0 && (
            <div className="mt-8">
              <h3 className="text-xl font-semibold mb-3">Expressions (Faste uttrykk)</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {data.expressions.map((expr, i) => (
                  <div key={i} className="border rounded-lg p-4 bg-gray-50 shadow-sm hover:shadow-md transition">
                    <p className="font-medium text-purple-700">{expr.phrase}</p>
                    <p className="text-sm text-gray-600 mt-1">{expr.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Save Buttons */}
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

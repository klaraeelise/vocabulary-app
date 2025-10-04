"use client";
import { useEffect, useState } from "react";

export default function AddWordPage() {
  const [languages, setLanguages] = useState([]);
  const [wordTypes, setWordTypes] = useState([]);
  const [word, setWord] = useState("");
  const [languageId, setLanguageId] = useState("");
  const [wordTypeId, setWordTypeId] = useState("");
  const [meanings, setMeanings] = useState([{ language_id: "", definition: "", note: "" }]);
  const [message, setMessage] = useState("");
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://vocabulary-app-python-service:8000";

  // Fetch languages & word types from backend
  useEffect(() => {
    fetch(`${API_BASE_URL}/languages`)
      .then(res => res.json())
      .then(data => setLanguages(data));

    fetch(`${API_BASE_URL}/word_types`)
      .then(res => res.json())
      .then(data => setWordTypes(data));
  }, []);

  const handleMeaningChange = (index: number, field: string, value: string) => {
    const updated = [...meanings];
    updated[index][field as keyof typeof updated[0]] = value;
    setMeanings(updated);
  };

  const addMeaning = () => {
    setMeanings([...meanings, { language_id: "", definition: "", note: "" }]);
  };

  const removeMeaning = (index: number) => {
    setMeanings(meanings.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = {
      word,
      wordtype_id: Number(wordTypeId),
      language_id: Number(languageId),
      meanings: meanings.map(m => ({
        language_id: Number(m.language_id),
        definition: m.definition,
        note: m.note || null,
      })),
    };

    const res = await fetch(`${API_BASE_URL}/words/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      setMessage("✅ Word added successfully!");
      setWord("");
      setLanguageId("");
      setWordTypeId("");
      setMeanings([{ language_id: "", definition: "", note: "" }]);
    } else {
      setMessage("❌ Failed to add word.");
    }
  };

  return (
    <div className="min-h-screen bg-ci_linen text-ci_black flex items-center justify-center">
      <div className="w-full max-w-2xl rounded-2xl bg-white shadow-lg p-8 border border-ci_brown">
        <h1 className="text-3xl font-bold text-center mb-6 text-ci_black">➕ Add a New Word</h1>

        {message && <p className="text-center mb-4 font-semibold">{message}</p>}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Word Input */}
          <div>
            <label className="block mb-1 font-semibold">Word</label>
            <input
              type="text"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              className="w-full p-2 border rounded bg-ci_linen text-ci_black"
              required
            />
          </div>

          {/* Language Dropdown */}
          <div>
            <label className="block mb-1 font-semibold">Language</label>
            <select
              value={languageId}
              onChange={(e) => setLanguageId(e.target.value)}
              className="w-full p-2 border rounded bg-ci_linen text-ci_black"
              required
            >
              <option value="">Select language</option>
              {languages.map((lang: any) => (
                <option key={lang.id} value={lang.id}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* Word Type Dropdown */}
          <div>
            <label className="block mb-1 font-semibold">Word Type</label>
            <select
              value={wordTypeId}
              onChange={(e) => setWordTypeId(e.target.value)}
              className="w-full p-2 border rounded bg-ci_linen text-ci_black"
              required
            >
              <option value="">Select word type</option>
              {wordTypes.map((type: any) => (
                <option key={type.id} value={type.id}>
                  {type.wordtype}
                </option>
              ))}
            </select>
          </div>

          

          {/* Meanings Section */}
          <div>
            <label className="block mb-2 font-semibold">Meanings</label>
            {meanings.map((m, index) => (
              <div key={index} className="border p-4 rounded mb-3 bg-ci_linen">
                <div className="flex gap-4 mb-2">
                  <select
                    value={m.language_id}
                    onChange={(e) => handleMeaningChange(index, "language_id", e.target.value)}
                    className="w-1/3 p-2 border rounded"
                    required
                  >
                    <option value="">Language</option>
                    {languages.map((lang: any) => (
                      <option key={lang.id} value={lang.id}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                  <input
                    type="text"
                    placeholder="Definition"
                    value={m.definition}
                    onChange={(e) => handleMeaningChange(index, "definition", e.target.value)}
                    className="flex-1 p-2 border rounded"
                    required
                  />
                </div>
                <input
                  type="text"
                  placeholder="Note (optional)"
                  value={m.note}
                  onChange={(e) => handleMeaningChange(index, "note", e.target.value)}
                  className="w-full p-2 border rounded"
                />
                {meanings.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeMeaning(index)}
                    className="text-ci_red mt-2 font-semibold"
                  >
                    Remove Meaning
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={addMeaning}
              className="mt-2 px-4 py-2 bg-ci_turquoise text-white rounded"
            >
              ➕ Add Another Meaning
            </button>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full py-2 bg-ci_yellow text-ci_black font-bold rounded hover:bg-ci_red hover:text-ci_linen transition"
          >
            Save Word
          </button>
        </form>
      </div>
    </div>
  );
}

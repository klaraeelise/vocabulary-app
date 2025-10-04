import { NextRequest, NextResponse } from "next/server";

// Dummy mapping functions—replace with your real logic/data!
const getWordtypeId = (category: string) => {
  // Map scraped category to your DB wordtype_id
  if (category === "substantiv") return 1; // Noun
  if (category === "verb") return 2;
  // ...etc
  return 1; // default to noun
};
const getLanguageId = (lang: string) => 1; // e.g. 1 for Norwegian

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { word, senses } = body;

  if (!word || !senses || !Array.isArray(senses) || senses.length === 0) {
    return NextResponse.json({ error: "Missing word or senses" }, { status: 400 });
  }

  // Use first sense for wordtype/category (customize as needed)
  const wordtype_id = getWordtypeId(senses[0].category);
  const language_id = getLanguageId("no"); // or get from UI/context

  // Flatten meanings from all senses
  const meanings: { language_id: number; definition: string; note?: string }[] = [];
  senses.forEach((sense) => {
    (sense.meanings || []).forEach((m: any) => {
      meanings.push({
        language_id,
        definition: m.description || m.definition || "", // adapt to your data shape!
        note: m.note || "",
      });
    });
  });

  // Build payload
  const payload = {
    word,
    wordtype_id,
    language_id,
    meanings,
  };

  // Send to Python backend
  const res = await fetch("http://python-service:8000/words/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok) {
    return NextResponse.json({ error: data.detail || "Save failed" }, { status: res.status });
  }

  return NextResponse.json(data);
}
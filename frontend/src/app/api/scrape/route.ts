import { NextResponse } from "next/server";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const word = searchParams.get("word");
  const language = searchParams.get("language") || "no-bm"; // Default to Norwegian Bokmål

  if (!word) {
    return NextResponse.json({ error: "Missing word" }, { status: 400 });
  }

  const res = await fetch(
    `http://vocabulary-app-go-service:8080/api/scrape?word=${encodeURIComponent(word)}&language=${encodeURIComponent(language)}`
  );
  if (!res.ok) {
    const errText = await res.text();
    return NextResponse.json({ error: errText || "Scraper failed" }, { status: res.status });
  }

  const data = await res.json();
  return NextResponse.json(data);
}

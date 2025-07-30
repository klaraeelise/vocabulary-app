// components/Flashcard.tsx
"use client";
import { useState } from "react";

interface FlashcardProps {
  word: string;
  meaning: string;
  example?: string;
}

export default function Flashcard({ word, meaning, example }: FlashcardProps) {
  const [flipped, setFlipped] = useState(false);

  return (
    <div
      onClick={() => setFlipped(!flipped)}
      className="w-64 h-40 flex items-center justify-center bg-kelp text-foam rounded-xl shadow-md cursor-pointer transform transition hover:scale-105"
    >
      {flipped ? (
        <div className="text-center">
          <p className="text-xl font-semibold">{meaning}</p>
          {example && <p className="mt-2 text-sm italic text-foam/80">"{example}"</p>}
        </div>
      ) : (
        <p className="text-2xl font-bold">{word}</p>
      )}
    </div>
  );
}

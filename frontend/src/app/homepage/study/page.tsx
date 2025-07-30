// app/dashboard/study/page.tsx
import Flashcard from "@/components/Flashcard";

const mockCards = [
  { word: "is", meaning: "ice", example: "Isen smelter." },
  { word: "hav", meaning: "sea", example: "Jeg liker havet." },
];

export default function StudyTodayPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Study Today</h1>
      <div className="flex flex-col items-center space-y-6">
        {mockCards.map((card, idx) => (
          <Flashcard key={idx} {...card} />
        ))}
      </div>
    </div>
  );
}

// app/dashboard/page.tsx
import VocabListCard from "@/components/VocabListCard";

const mockLists = [
  { id: 1, name: "Norwegian Basics", progress: 40, total: 50 },
  { id: 2, name: "Advanced Verbs", progress: 10, total: 30 },
];

export default function DashboardPage() {
  return (
    <div className="p-6">
      <h1 className="mb-4 text-3xl font-bold">Your Vocabulary Lists</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {mockLists.map((list) => (
          <VocabListCard key={list.id} {...list} />
        ))}
      </div>
    </div>
  );
}

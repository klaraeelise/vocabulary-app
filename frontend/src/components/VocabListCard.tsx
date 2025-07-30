// components/VocabListCard.tsx
import ProgressBar from "./ProgressBar";
import Link from "next/link";

interface VocabListCardProps {
  id: number;
  name: string;
  progress: number;
  total: number;
}

export default function VocabListCard({ id, name, progress, total }: VocabListCardProps) {
  return (
    <div className="rounded-xl bg-kelp p-4 shadow-lg hover:shadow-xl transition">
      <h2 className="text-xl font-bold mb-2">{name}</h2>
      <p className="text-sm mb-2 text-foam">{progress}/{total} words learned</p>
      <ProgressBar value={Math.round((progress / total) * 100)} />
      <Link
        href={`/dashboard/study?list=${id}`}
        className="mt-3 inline-block text-sm text-glow hover:underline"
      >
        Study this list →
      </Link>
    </div>
  );
}

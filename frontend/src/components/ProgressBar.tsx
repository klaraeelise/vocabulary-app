// components/ProgressBar.tsx
interface ProgressBarProps {
  value: number;
}

export default function ProgressBar({ value }: ProgressBarProps) {
  return (
    <div className="w-full bg-foam/30 rounded-full h-3">
      <div
        className="bg-glow h-3 rounded-full transition-all duration-300"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

interface DivinationCardProps {
  panResult: string;
}

export default function DivinationCard({ panResult }: DivinationCardProps) {
  return (
    <div className="card flex flex-col h-full m-1">
      <div className="flex-1 overflow-y-auto p-4 font-mono text-sm leading-relaxed
                      whitespace-pre-wrap break-all overflow-x-hidden">
        {panResult}
      </div>
    </div>
  );
}

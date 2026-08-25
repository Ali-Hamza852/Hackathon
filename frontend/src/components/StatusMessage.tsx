interface StatusMessageProps {
  message: string;
  subtext?: string;
}

export function LoadingState({ message }: StatusMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white py-16 text-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-emerald-600" />
      <p className="text-sm font-medium text-slate-500">{message}</p>
    </div>
  );
}

export function ErrorState({ message, subtext }: StatusMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-red-200 bg-red-50 py-16 text-center">
      <p className="text-2xl">⚠️</p>
      <p className="text-sm font-semibold text-red-800">{message}</p>
      {subtext && <p className="max-w-sm text-xs text-red-600">{subtext}</p>}
    </div>
  );
}

export function EmptyState({ message, subtext }: StatusMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white py-16 text-center">
      <p className="text-2xl">🌤️</p>
      <p className="text-sm font-semibold text-slate-700">{message}</p>
      {subtext && <p className="max-w-sm text-xs text-slate-500">{subtext}</p>}
    </div>
  );
}

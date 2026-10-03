export default function Spinner({ label = "Loading…" }) {
  return (
    <div className="flex items-center justify-center py-10 text-gray-500 gap-3">
      <div className="w-5 h-5 border-2 border-navy-700 border-t-transparent rounded-full animate-spin" />
      <span>{label}</span>
    </div>
  );
}
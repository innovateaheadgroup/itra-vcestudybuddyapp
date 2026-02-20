export function CommandTermBadge({ term }: { term: string }) {
  return (
    <span className="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-semibold text-purple-700">
      {term}
    </span>
  )
}

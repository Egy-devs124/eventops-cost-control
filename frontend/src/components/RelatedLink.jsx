import { Link } from "react-router-dom";

export function RelatedLink({ to, label }) {
  if (!label) return <span>-</span>;
  if (!to) return <span>{label}</span>;
  return (
    <Link className="related-link" to={to}>
      {label}
    </Link>
  );
}

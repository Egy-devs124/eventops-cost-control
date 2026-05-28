export function ChartCard({ title, children }) {
  return (
    <section className="chart-card">
      <h2>{title}</h2>
      <div className="chart-body">{children}</div>
    </section>
  );
}

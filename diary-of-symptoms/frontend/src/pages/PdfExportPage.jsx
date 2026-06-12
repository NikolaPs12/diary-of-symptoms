import { CalendarDays, Download } from "lucide-react";
import SectionHeader from "../components/SectionHeader";

function QuickRangeButton({ label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="border border-diary-line px-4 py-3 text-sm transition hover:bg-diary-black hover:text-diary-white"
    >
      {label}
    </button>
  );
}

export default function PdfExportPage({
  copy,
  startDate,
  endDate,
  onDateChange,
  onExportRange,
  onExportWeek,
  onExportMonth,
  onExportAll,
  status,
}) {
  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow={copy.pdf.eyebrow}
        title={copy.pdf.title}
        description={copy.pdf.description}
      />

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <section className="surface p-5 md:p-6">
          <div className="grid gap-4 md:grid-cols-[1fr_1fr_auto] md:items-end">
            <label className="grid gap-2">
              <span className="text-xs uppercase tracking-[0.24em] text-diary-muted">
                {copy.pdf.from}
              </span>
              <div className="flex items-center gap-3 border border-diary-line px-4 py-3">
                <CalendarDays className="h-4 w-4" />
                <input
                  className="w-full bg-transparent text-sm outline-none"
                  type="date"
                  name="startDate"
                  value={startDate}
                  onChange={onDateChange}
                />
              </div>
            </label>

            <label className="grid gap-2">
              <span className="text-xs uppercase tracking-[0.24em] text-diary-muted">
                {copy.pdf.to}
              </span>
              <div className="flex items-center gap-3 border border-diary-line px-4 py-3">
                <CalendarDays className="h-4 w-4" />
                <input
                  className="w-full bg-transparent text-sm outline-none"
                  type="date"
                  name="endDate"
                  value={endDate}
                  onChange={onDateChange}
                />
              </div>
            </label>

            <button
              type="button"
              onClick={onExportRange}
              className="inline-flex items-center justify-center gap-2 border border-diary-black bg-diary-black px-5 py-3 text-sm font-medium text-diary-white transition hover:bg-diary-white hover:text-diary-black"
            >
              <Download className="h-4 w-4" />
              {copy.pdf.generate}
            </button>
          </div>

          <div className="mt-4 flex flex-wrap gap-3">
            <QuickRangeButton label={copy.pdf.week} onClick={onExportWeek} />
            <QuickRangeButton label={copy.pdf.month} onClick={onExportMonth} />
            <QuickRangeButton label={copy.pdf.allData} onClick={onExportAll} />
          </div>

          {status ? (
            <div className="mt-4 border border-diary-line bg-diary-panel px-4 py-3 text-sm">
              {status}
            </div>
          ) : null}
        </section>

        <aside className="surface-muted p-5">
          <div className="text-xs uppercase tracking-[0.24em] text-diary-muted">
            {copy.pdf.howItWorks}
          </div>
          <div className="mt-5 space-y-4 text-sm leading-6">
            {copy.pdf.steps.map((step, index) => (
              <div key={step} className="flex gap-4 border-b border-diary-line pb-4 last:border-b-0">
                <div className="font-mono text-sm">{String(index + 1).padStart(2, "0")}</div>
                <div>{step}</div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}


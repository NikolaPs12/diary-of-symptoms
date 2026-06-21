import { useState } from "react";
import { Activity, ArrowRight } from "lucide-react";
import SectionHeader from "../components/SectionHeader";

function SliderField({ label, name, value, onChange }) {
  return (
    <div className="surface p-5">
      <div className="mb-4 flex items-end justify-between gap-3">
        <div className="text-sm font-medium">{label}</div>
        <div className="font-mono text-xl">{value}/10</div>
      </div>
      <input
        className="range-shell"
        type="range"
        min="0"
        max="10"
        name={name}
        value={value}
        onChange={onChange}
      />
    </div>
  );
}

const createInitialForm = () => ({
  severity: 5,
  sleep_quality: 6,
  sleep_hours: 7,
  stress_level: 5,
  notes: "",
  food_notes: "",
  medications_taken: "",
});

export default function HealthStatePage({ onSubmitEntry, copy }) {
  const [form, setForm] = useState(createInitialForm);
  const [status, setStatus] = useState("idle");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]:
        name === "severity" ||
        name === "sleep_quality" ||
        name === "sleep_hours" ||
        name === "stress_level"
          ? Number(value)
          : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus("submitting");
    await onSubmitEntry({
      ...form,
      symptom: "daily check-in",
      duration: "1d",
      start_at: new Date().toISOString(),
    });
    setStatus("done");
    setForm(createInitialForm());
  };

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow={copy.entry.eyebrow}
        title={copy.dashboard.healthState}
        description={copy.entry.description}
      />

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="surface grid gap-4 p-5 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-diary-muted">
                {copy.entry.sleepHours}
              </label>
              <input
                className="field-shell w-full font-mono"
                name="sleep_hours"
                type="number"
                min="0"
                max="24"
                step="0.5"
                value={form.sleep_hours}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <SliderField label={copy.entry.severity} name="severity" value={form.severity} onChange={handleChange} />
            <SliderField label={copy.entry.stress} name="stress_level" value={form.stress_level} onChange={handleChange} />
            <SliderField
              label={copy.entry.sleepQuality}
              name="sleep_quality"
              value={form.sleep_quality}
              onChange={handleChange}
            />
          </div>

          <div className="surface grid gap-4 p-5">
            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-diary-muted">
                {copy.entry.notes}
              </label>
              <textarea
                className="field-shell min-h-32 w-full resize-none"
                name="notes"
                value={form.notes}
                onChange={handleChange}
                placeholder={copy.entry.notesPlaceholder}
              />
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-diary-muted">
                {copy.entry.foodNotes}
              </label>
              <textarea
                className="field-shell min-h-32 w-full resize-none"
                name="food_notes"
                value={form.food_notes}
                onChange={handleChange}
                placeholder={copy.entry.foodPlaceholder}
              />
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-diary-muted">
                {copy.entry.medicationsTaken}
              </label>
              <textarea
                className="field-shell min-h-32 w-full resize-none"
                name="medications_taken"
                value={form.medications_taken}
                onChange={handleChange}
                placeholder={copy.entry.medicationPlaceholder}
              />
            </div>
          </div>

          <button
            type="submit"
            className="inline-flex items-center gap-3 border border-diary-black bg-diary-black px-5 py-3 text-sm font-medium text-diary-white transition hover:bg-diary-white hover:text-diary-black"
          >
            <Activity className="h-4 w-4" />
            {status === "submitting" ? copy.entry.saving : copy.entry.saveHealthState}
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <aside className="space-y-4">
          <div className="surface-muted p-5">
            <div className="text-xs uppercase tracking-[0.24em] text-diary-muted">
              {copy.entry.structure}
            </div>
            <div className="mt-5 space-y-4">
              {copy.entry.structureItems.map((item, index) => (
                <div key={item} className="flex gap-4 border-b border-diary-line pb-4 last:border-b-0">
                  <div className="font-mono text-sm">{String(index + 1).padStart(2, "0")}</div>
                  <div className="text-sm leading-6">{item}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="surface p-5">
            <div className="mb-4 text-xs uppercase tracking-[0.24em] text-diary-muted">
              {copy.entry.output}
            </div>
            <p className="text-sm leading-6 text-diary-muted">{copy.entry.outputPlaceholder}</p>
          </div>
        </aside>
      </div>
    </div>
  );
}

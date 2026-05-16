import { useState } from "react";
import { ArrowRight, BrainCircuit } from "lucide-react";
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
  start_at: new Date().toISOString().slice(0, 16),
  symptom: "",
  body_state: "",
  severity: 5,
  duration: "2h",
  sleep_quality: 6,
  sleep_hours: 7,
  stress_level: 5,
  notes: "",
  food_notes: "",
  medications_taken: "",
});

export default function SymptomEntryPage({ onSubmitEntry, copy }) {
  const [form, setForm] = useState(createInitialForm);
  const [insight, setInsight] = useState("");
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
    setInsight(""); // Очищаем старый инсайт перед новым запросом
    setStatus("submitting");
    const entry = await onSubmitEntry(form);
    setInsight(entry.ai_insights);
    setStatus("done");
    setForm(createInitialForm());
  };

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow={copy.entry.eyebrow}
        title={copy.entry.title}
        description={copy.entry.description}
      />

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="surface grid gap-4 p-5 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
                {copy.entry.symptom}
              </label>
              <input
                className="field-shell w-full"
                name="symptom"
                value={form.symptom}
                onChange={handleChange}
                placeholder={copy.entry.symptomPlaceholder}
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
                {copy.entry.bodyState}
              </label>
              <textarea
                className="field-shell min-h-28 w-full resize-none"
                name="body_state"
                value={form.body_state}
                onChange={handleChange}
                placeholder={copy.entry.bodyStatePlaceholder}
              />
            </div>

            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
                {copy.entry.startedAt}
              </label>
              <input
                className="field-shell w-full font-mono"
                name="start_at"
                type="datetime-local"
                value={form.start_at}
                onChange={handleChange}
              />
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
                {copy.entry.duration}
              </label>
              <input
                className="field-shell w-full font-mono"
                name="duration"
                value={form.duration}
                onChange={handleChange}
                placeholder={copy.entry.durationPlaceholder}
                required
              />
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
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
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
                {copy.entry.foodNotes}
              </label>
              <textarea
                className="field-shell min-h-24 w-full resize-none"
                name="food_notes"
                value={form.food_notes}
                onChange={handleChange}
                placeholder={copy.entry.foodPlaceholder}
              />
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
                {copy.entry.medicationsTaken}
              </label>
              <textarea
                className="field-shell min-h-24 w-full resize-none"
                name="medications_taken"
                value={form.medications_taken}
                onChange={handleChange}
                placeholder={copy.entry.medicationPlaceholder}
              />
            </div>
            <div>
              <label className="mb-2 block text-xs uppercase tracking-[0.24em] text-codex-muted">
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
          </div>

          <button
            type="submit"
            className="inline-flex items-center gap-3 border border-codex-black bg-codex-black px-5 py-3 text-sm font-medium text-codex-white transition hover:bg-codex-white hover:text-codex-black"
          >
            <BrainCircuit className="h-4 w-4" />
            {status === "submitting" ? copy.entry.analyzing : copy.entry.analyze}
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <aside className="space-y-4">
          <div className="surface-muted p-5">
            <div className="text-xs uppercase tracking-[0.24em] text-codex-muted">
              {copy.entry.structure}
            </div>
            <div className="mt-5 space-y-4">
              {copy.entry.structureItems.map((item, index) => (
                <div key={item} className="flex gap-4 border-b border-codex-line pb-4 last:border-b-0">
                  <div className="font-mono text-sm">{String(index + 1).padStart(2, "0")}</div>
                  <div className="text-sm leading-6">{item}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="surface p-5">
            <div className="mb-4 text-xs uppercase tracking-[0.24em] text-codex-muted">
              {copy.entry.output}
            </div>
            {insight ? (
              /* ИСПРАВЛЕННЫЙ БЛОК: Отрисовываем HTML от нейронки */
              <div 
                className="prose prose-sm max-w-none border-l-4 border-l-codex-black pl-4 text-sm leading-7"
                dangerouslySetInnerHTML={{ __html: insight }} 
              />
            ) : (
              <p className="text-sm leading-6 text-codex-muted">{copy.entry.outputPlaceholder}</p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
import { useEffect, useState } from "react";
import SectionHeader from "../components/SectionHeader";
import { buildThemePreview, themeDefinitions, themeOrder } from "../lib/themes";

function ThemePreviewCard({ themeId, isActive, copy, onApply }) {
  const theme = themeDefinitions[themeId];
  const preview = buildThemePreview(themeId);

  return (
    <article className={`theme-card ${isActive ? "theme-card-active" : ""}`}>
      <div
        className="border-b p-4"
        style={{
          background: preview.background,
          borderColor: preview.border,
        }}
      >
        <div className="grid gap-3">
          <div className="flex items-center justify-between">
            <div className="text-[11px] uppercase tracking-[0.24em]" style={{ color: preview.text }}>
              {copy.appearance.previewLabel}
            </div>
            <div
              className="rounded-full border px-2 py-1 text-[10px] uppercase tracking-[0.24em]"
              style={{
                color: preview.text,
                borderColor: preview.border,
                background: preview.surface,
              }}
            >
              {isActive ? copy.appearance.applied : copy.appearance.apply}
            </div>
          </div>

          <div
            className="rounded-xl border p-3"
            style={{
              borderColor: preview.border,
              background: preview.surface,
              boxShadow: "0 10px 24px rgba(15, 23, 42, 0.08)",
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold" style={{ color: preview.text }}>
                  Health Snapshot
                </div>
                <div className="mt-1 text-xs" style={{ color: preview.text, opacity: 0.7 }}>
                  Calm symptom overview
                </div>
              </div>
              <div
                className="h-10 w-10 rounded-full"
                style={{ background: preview.accent, opacity: 0.9 }}
              />
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2">
              {[72, 54, 81].map((value, index) => (
                <div
                  key={value}
                  className="rounded-lg border p-2"
                  style={{
                    borderColor: preview.border,
                    background: preview.surface,
                  }}
                >
                  <div className="text-[10px] uppercase" style={{ color: preview.text, opacity: 0.62 }}>
                    {index === 0 ? "Severity" : index === 1 ? "Sleep" : "Stress"}
                  </div>
                  <div className="mt-2 text-sm font-semibold" style={{ color: preview.text }}>
                    {value}
                  </div>
                  <div
                    className="mt-2 h-1.5 rounded-full"
                    style={{ background: preview.border }}
                  >
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${Math.min(value, 100)}%`, background: preview.accent }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-4 p-5">
        <div>
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-lg font-semibold tracking-swiss text-diary-black">
              {copy.appearance.themes[themeId].name}
            </h3>
            {isActive ? (
              <span className="rounded-full bg-diary-accentSoft px-3 py-1 text-[10px] uppercase tracking-[0.24em] text-diary-black">
                {copy.appearance.active}
              </span>
            ) : null}
          </div>
          <p className="mt-2 text-sm leading-6 text-diary-muted">
            {copy.appearance.themes[themeId].description}
          </p>
        </div>

        <div className="grid gap-3 text-sm text-diary-muted">
          <div>
            <span className="text-diary-black">{copy.appearance.idea}: </span>
            {theme.idea}
          </div>
          <div>
            <span className="text-diary-black">{copy.appearance.whenToUse}: </span>
            {theme.whenToUse}
          </div>
        </div>

        <button
          type="button"
          onClick={() => onApply(themeId)}
          className={`w-full border px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.28em] transition ${
            isActive
              ? "border-diary-black bg-diary-black text-white"
              : "border-diary-line text-diary-black hover:border-diary-black hover:bg-diary-black hover:text-white"
          }`}
        >
          {isActive ? copy.appearance.applied : copy.appearance.apply}
        </button>
      </div>
    </article>
  );
}

export default function ProfilePage({
  currentUser,
  profileCard,
  copy,
  theme,
  onThemeChange,
  onSaveProfileCard,
}) {
  const [form, setForm] = useState({
    name: currentUser?.name ?? "",
    weight: currentUser?.weight ?? "",
    height: currentUser?.height ?? "",
    medication_name: profileCard?.name ?? "",
    dosage: profileCard?.dosage ?? "",
    diagnosis: profileCard?.diagnosis ?? "",
    allergies: profileCard?.allergies?.join(", ") ?? "",
    notes: profileCard?.notes ?? "",
    puls_is_normal: currentUser?.puls_is_normal ?? profileCard?.puls_is_normal ?? 70,
    pressure_is_normal: currentUser?.pressure_is_normal ?? profileCard?.pressure_is_normal ?? "120/80",
  });

  const [status, setStatus] = useState("");

  useEffect(() => {
    setForm({
      name: currentUser?.name ?? "",
      weight: currentUser?.weight ?? "",
      height: currentUser?.height ?? "",
      medication_name: profileCard?.name ?? "",
      dosage: profileCard?.dosage ?? "",
      diagnosis: profileCard?.diagnosis ?? "",
      allergies: profileCard?.allergies?.join(", ") ?? "",
      notes: profileCard?.notes ?? "",
      puls_is_normal: currentUser?.puls_is_normal ?? profileCard?.puls_is_normal ?? 70,
      pressure_is_normal: currentUser?.pressure_is_normal ?? profileCard?.pressure_is_normal ?? "120/80",
    });
  }, [currentUser, profileCard]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handlePulseChange = (delta) => {
    setForm((prev) => ({
      ...prev,
      puls_is_normal: Math.max(40, Math.min(220, Number(prev.puls_is_normal) + delta)),
    }));
  };

  const handlePressureSlider = (value, type) => {
    const [sys, dia] = form.pressure_is_normal.split("/");
    if (type === "sys") {
      setForm((prev) => ({ ...prev, pressure_is_normal: `${value}/${dia}` }));
    } else {
      setForm((prev) => ({ ...prev, pressure_is_normal: `${sys}/${value}` }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await onSaveProfileCard({
      ...form,
      allergies: form.allergies
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      puls_is_normal: parseInt(form.puls_is_normal, 10),
    });
    setStatus(copy.profile.cardSaved);
  };

  return (
    <div className="mx-auto max-w-6xl space-y-12 pb-20">
      <SectionHeader
        eyebrow={copy.profile.eyebrow}
        title={copy.profile.title}
        description={copy.profile.description}
      />

      <div className="grid items-start gap-12 xl:grid-cols-[1fr_1fr]">
        <form className="space-y-10" onSubmit={handleSubmit}>
          <section className="space-y-4">
            <h3 className="border-b border-diary-line pb-2 text-[10px] font-bold uppercase tracking-[0.3em] text-diary-muted">
              Личные данные
            </h3>
            <div className="grid gap-4">
              <input className="field-shell" name="name" value={form.name} onChange={handleChange} placeholder="ФИО пациента" />
              <div className="grid grid-cols-2 gap-4">
                <div className="relative">
                  <input className="field-shell w-full pr-10" name="weight" type="number" value={form.weight} onChange={handleChange} placeholder="Вес" />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] uppercase text-diary-muted">kg</span>
                </div>
                <div className="relative">
                  <input className="field-shell w-full pr-10" name="height" type="number" value={form.height} onChange={handleChange} placeholder="Рост" />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] uppercase text-diary-muted">cm</span>
                </div>
              </div>
            </div>
          </section>

          <section className="space-y-4">
            <h3 className="border-b border-diary-line pb-2 text-[10px] font-bold uppercase tracking-[0.3em] text-diary-muted">
              Медицинские показатели
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <input className="field-shell" name="medication_name" value={form.medication_name} onChange={handleChange} placeholder="Препарат" />
              <input className="field-shell font-mono" name="dosage" value={form.dosage} onChange={handleChange} placeholder="Дозировка" />
            </div>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="field-shell flex flex-col items-center bg-transparent py-4">
                <span className="mb-2 text-[9px] uppercase tracking-widest text-diary-muted">Пульс (цель)</span>
                <div className="flex items-center gap-4">
                  <button type="button" onClick={() => handlePulseChange(-1)} className="text-xl transition hover:text-diary-accent">–</button>
                  <span className="text-2xl font-mono text-diary-black">{form.puls_is_normal}</span>
                  <button type="button" onClick={() => handlePulseChange(1)} className="text-xl transition hover:text-diary-accent">+</button>
                </div>
              </div>
              <div className="field-shell flex flex-col items-center bg-transparent py-4">
                <span className="mb-2 text-[9px] uppercase tracking-widest text-diary-muted">АД (цель)</span>
                <span className="text-2xl font-mono text-diary-black">{form.pressure_is_normal}</span>
              </div>
            </div>
            <textarea className="field-shell min-h-[100px] w-full resize-none py-3" name="notes" value={form.notes} onChange={handleChange} placeholder="Дополнительные примечания..." />
          </section>

          <button type="submit" className="w-full bg-diary-black py-4 text-[11px] font-bold uppercase tracking-[0.3em] text-white transition-all duration-300 hover:bg-diary-accent">
            Обновить медицинский профиль
          </button>
          {status && <p className="animate-pulse text-center text-[10px] text-diary-muted">{status}</p>}
        </form>

        <div className="sticky top-10 space-y-8">
          <div className="surface border border-diary-line bg-white/[0.02] p-8 space-y-8">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-2xl font-light tracking-tight text-diary-black">{form.name || "Nikola P. O."}</h2>
                <p className="mt-1 text-xs uppercase tracking-widest text-diary-muted">Medical ID card</p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-mono text-diary-accent">{form.weight || "—"}</span>
                <span className="ml-1 text-[10px] uppercase text-diary-muted">kg</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-px border border-diary-line bg-diary-line">
              <div className="p-4">
                <p className="mb-1 text-[9px] font-bold uppercase tracking-tighter text-diary-muted">Текущий курс</p>
                <p className="text-sm font-medium text-diary-black">{profileCard?.name || "Не назначено"}</p>
              </div>
              <div className="p-4">
                <p className="mb-1 text-[9px] font-bold uppercase tracking-tighter text-diary-muted">Дозировка</p>
                <p className="text-sm font-mono text-diary-black">{profileCard?.dosage || "—"}</p>
              </div>
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <div className="flex justify-between text-[10px] uppercase tracking-widest text-diary-muted">
                  <span>Целевое давление</span>
                  <span className="font-mono text-diary-accent">{form.pressure_is_normal}</span>
                </div>
                <div className="space-y-4 pt-2">
                  <div className="relative flex h-6 items-center">
                    <input
                      type="range"
                      min="80"
                      max="180"
                      value={form.pressure_is_normal.split("/")[0]}
                      onChange={(event) => handlePressureSlider(event.target.value, "sys")}
                      className="range-shell w-full"
                    />
                    <span className="absolute -top-3 left-0 text-[8px] uppercase text-diary-muted">Систола</span>
                  </div>
                  <div className="relative flex h-6 items-center">
                    <input
                      type="range"
                      min="50"
                      max="120"
                      value={form.pressure_is_normal.split("/")[1]}
                      onChange={(event) => handlePressureSlider(event.target.value, "dia")}
                      className="range-shell w-full"
                    />
                    <span className="absolute -top-3 left-0 text-[8px] uppercase text-diary-muted">Диастола</span>
                  </div>
                </div>
              </div>
            </div>

            {profileCard?.notes && (
              <div className="border-t border-diary-line pt-4">
                <p className="mb-2 text-[9px] font-bold uppercase tracking-widest text-diary-muted">Заметки врача</p>
                <p className="text-xs italic leading-relaxed text-diary-muted">{profileCard.notes}</p>
              </div>
            )}
          </div>

          <section className="space-y-6">
            <SectionHeader
              eyebrow={copy.appearance.eyebrow}
              title={copy.appearance.title}
              description={copy.appearance.description}
            />

            <div className="surface-muted p-5">
              <div className="text-xs uppercase tracking-[0.24em] text-diary-muted">{copy.appearance.tokensTitle}</div>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {copy.appearance.tokens.map((item) => (
                  <div key={item} className="surface bg-transparent px-4 py-3 text-sm text-diary-muted">
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <div className="text-xs uppercase tracking-[0.24em] text-diary-muted">{copy.appearance.sectionTitle}</div>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-diary-muted">
                  {copy.appearance.sectionDescription}
                </p>
              </div>

              <div className="grid gap-5 xl:grid-cols-2">
                {themeOrder.map((themeId) => (
                  <ThemePreviewCard
                    key={themeId}
                    themeId={themeId}
                    isActive={theme === themeId}
                    copy={copy}
                    onApply={onThemeChange}
                  />
                ))}
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

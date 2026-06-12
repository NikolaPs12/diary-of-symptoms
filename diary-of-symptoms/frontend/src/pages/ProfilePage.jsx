import { useEffect, useState } from "react";
import SectionHeader from "../components/SectionHeader";

export default function ProfilePage({ currentUser, profileCard, copy, onSaveProfileCard }) {
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
    setForm(prev => ({
      ...prev,
      puls_is_normal: Math.max(40, Math.min(220, Number(prev.puls_is_normal) + delta))
    }));
  };

  const handlePressureSlider = (value, type) => {
    const [sys, dia] = form.pressure_is_normal.split('/');
    if (type === 'sys') {
      setForm(prev => ({ ...prev, pressure_is_normal: `${value}/${dia}` }));
    } else {
      setForm(prev => ({ ...prev, pressure_is_normal: `${sys}/${value}` }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await onSaveProfileCard({
      ...form,
      allergies: form.allergies.split(",").map((item) => item.trim()).filter(Boolean),
      puls_is_normal: parseInt(form.puls_is_normal),
    });
    setStatus(copy.profile.cardSaved);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-12 pb-20">
      <SectionHeader
        eyebrow={copy.profile.eyebrow}
        title={copy.profile.title}
        description={copy.profile.description}
      />

      <div className="grid gap-12 xl:grid-cols-[1fr_1fr] items-start">
        
        {/* ЛЕВАЯ ЧАСТЬ: РЕДАКТИРОВАНИЕ */}
        <form className="space-y-10" onSubmit={handleSubmit}>
          
          <section className="space-y-4">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.3em] text-diary-muted border-b border-diary-line pb-2">
              Личные данные
            </h3>
            <div className="grid gap-4">
              <input className="field-shell" name="name" value={form.name} onChange={handleChange} placeholder="ФИО пациента" />
              <div className="grid grid-cols-2 gap-4">
                <div className="relative">
                  <input className="field-shell w-full pr-10" name="weight" type="number" value={form.weight} onChange={handleChange} placeholder="Вес" />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-diary-muted uppercase">kg</span>
                </div>
                <div className="relative">
                  <input className="field-shell w-full pr-10" name="height" type="number" value={form.height} onChange={handleChange} placeholder="Рост" />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-diary-muted uppercase">cm</span>
                </div>
              </div>
            </div>
          </section>

          <section className="space-y-4">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.3em] text-diary-muted border-b border-diary-line pb-2">
              Медицинские показатели
            </h3>
            <div className="grid grid-cols-2 gap-4">
               <input className="field-shell" name="medication_name" value={form.medication_name} onChange={handleChange} placeholder="Препарат" />
               <input className="field-shell font-mono" name="dosage" value={form.dosage} onChange={handleChange} placeholder="Дозировка" />
            </div>
            <div className="grid grid-cols-2 gap-4 text-center">
               <div className="field-shell flex flex-col items-center py-4 bg-white/5">
                  <span className="text-[9px] uppercase tracking-widest text-diary-muted mb-2">Пульс (цель)</span>
                  <div className="flex items-center gap-4">
                    <button type="button" onClick={() => handlePulseChange(-1)} className="hover:text-diary-accent transition text-xl">–</button>
                    <span className="text-2xl font-mono">{form.puls_is_normal}</span>
                    <button type="button" onClick={() => handlePulseChange(1)} className="hover:text-diary-accent transition text-xl">+</button>
                  </div>
               </div>
               <div className="field-shell flex flex-col items-center py-4 bg-white/5">
                  <span className="text-[9px] uppercase tracking-widest text-diary-muted mb-2">АД (цель)</span>
                  <span className="text-2xl font-mono">{form.pressure_is_normal}</span>
               </div>
            </div>
            <textarea className="field-shell w-full min-h-[100px] py-3 resize-none" name="notes" value={form.notes} onChange={handleChange} placeholder="Дополнительные примечания..." />
          </section>

          <button type="submit" className="w-full bg-diary-black text-diary-white py-4 text-[11px] font-bold uppercase tracking-[0.3em] hover:bg-diary-accent transition-all duration-300">
            Обновить медицинский профиль
          </button>
          {status && <p className="text-center text-[10px] text-diary-muted animate-pulse">{status}</p>}
        </form>

        {/* ПРАВАЯ ЧАСТЬ: ВИЗУАЛЬНАЯ КАРТОЧКА */}
        <div className="sticky top-10">
          <div className="surface border border-diary-line p-8 space-y-8 bg-white/[0.02]">
            <div className="flex justify-between items-start">
               <div>
                 <h2 className="text-2xl font-light tracking-tight">{form.name || "Nikola P. O."}</h2>
                 <p className="text-xs text-diary-muted mt-1 uppercase tracking-widest">Medical ID card</p>
               </div>
               <div className="text-right">
                  <span className="text-2xl font-mono text-diary-accent">{form.weight || "—"}</span>
                  <span className="text-[10px] text-diary-muted uppercase ml-1">kg</span>
               </div>
            </div>

            <div className="grid grid-cols-2 gap-px bg-diary-line border border-diary-line">
               <div className=" p-4">
                  <p className="text-[9px] uppercase tracking-tighter text-diary-muted mb-1 font-bold">Текущий курс</p>
                  <p className="text-sm font-medium">{profileCard?.name || "Не назначено"}</p>
               </div>
               <div className=" p-4">
                  <p className="text-[9px] uppercase tracking-tighter text-diary-muted mb-1 font-bold">Дозировка</p>
                  <p className="text-sm font-mono">{profileCard?.dosage || "—"}</p>
               </div>
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <div className="flex justify-between text-[10px] uppercase tracking-widest text-diary-muted">
                  <span>Целевое давление</span>
                  <span className="font-mono text-diary-accent">{form.pressure_is_normal}</span>
                </div>
                <div className="space-y-4 pt-2">
                  <div className="relative h-6 flex items-center">
                    <input 
                      type="range" min="80" max="180" 
                      value={form.pressure_is_normal.split('/')[0]} 
                      onChange={(e) => handlePressureSlider(e.target.value, 'sys')}
                      className="w-full h-px bg-diary-line appearance-none cursor-pointer accent-diary-black [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-diary-accent [&::-webkit-slider-thumb]:rounded-full"
                    />
                    <span className="absolute -top-3 left-0 text-[8px] text-diary-muted uppercase">Систола</span>
                  </div>
                  <div className="relative h-6 flex items-center">
                    <input 
                      type="range" min="50" max="120" 
                      value={form.pressure_is_normal.split('/')[1]} 
                      onChange={(e) => handlePressureSlider(e.target.value, 'dia')}
                      className="w-full h-px bg-diary-line appearance-none cursor-pointer accent-diary-black [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border [&::-webkit-slider-thumb]:border-diary-line [&::-webkit-slider-thumb]:rounded-full"
                    />
                    <span className="absolute -top-3 left-0 text-[8px] text-diary-muted uppercase">Диастола</span>
                  </div>
                </div>
              </div>
            </div>

            {profileCard?.notes && (
              <div className="pt-4 border-t border-diary-line">
                <p className="text-[9px] uppercase tracking-widest text-diary-muted mb-2 font-bold">Заметки врача</p>
                <p className="text-xs leading-relaxed italic text-diary-muted">{profileCard.notes}</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

import { useEffect, useMemo, useState } from "react";
import SectionHeader from "../components/SectionHeader";

const CHANNELS = {
  telegram: "telegram",
  email: "email",
};

const WEEKDAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DEFAULT_TEMPLATE = "Не забудьте отметить симптомы в дневнике.";

function buildInitialForm() {
  return {
    id: null,
    title: "",
    message: DEFAULT_TEMPLATE,
    send_time: "09:00",
    weekdays: [],
    channel: CHANNELS.telegram,
    enable: true,
  };
}

function sortWeekdays(weekdays) {
  return [...weekdays].sort(
    (first, second) => WEEKDAY_ORDER.indexOf(first) - WEEKDAY_ORDER.indexOf(second),
  );
}

function formatSchedule(reminder, copy) {
  const time = reminder.send_time || "--:--";
  const labels = reminder.weekdays?.length
    ? reminder.weekdays.map((day) => copy.notifications.weekdays[day]).join(", ")
    : copy.notifications.everyDay;
  return `${time} · ${labels}`;
}

function detectChannel(reminder) {
  if (reminder.send_email) {
    return CHANNELS.email;
  }
  return CHANNELS.telegram;
}

export default function NotificationsPage({
  copy,
  reminders,
  onCreateReminder,
  onUpdateReminder,
  onDeleteReminder,
  onToggleReminder,
}) {
  const [form, setForm] = useState(buildInitialForm);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [listError, setListError] = useState("");

  useEffect(() => {
    setStatus("");
    setError("");
    setListError("");
  }, [form.id]);

  const sortedReminders = useMemo(
    () =>
      [...reminders].sort((first, second) => {
        const firstTime = first.next_send_at ? new Date(first.next_send_at).getTime() : Number.MAX_SAFE_INTEGER;
        const secondTime = second.next_send_at ? new Date(second.next_send_at).getTime() : Number.MAX_SAFE_INTEGER;
        return firstTime - secondTime;
      }),
    [reminders],
  );

  const resetForm = () => {
    setForm(buildInitialForm());
    setStatus("");
    setError("");
  };

  const handleFieldChange = (event) => {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleWeekdayToggle = (weekday) => {
    setForm((current) => {
      const nextWeekdays = current.weekdays.includes(weekday)
        ? current.weekdays.filter((item) => item !== weekday)
        : sortWeekdays([...current.weekdays, weekday]);

      return {
        ...current,
        weekdays: nextWeekdays,
      };
    });
  };

  const handleEdit = (reminder) => {
    setForm({
      id: reminder.id,
      title: reminder.title,
      message: reminder.message,
      send_time: reminder.send_time || "09:00",
      weekdays: reminder.weekdays || [],
      channel: detectChannel(reminder),
      enable: reminder.enable,
    });
  };

  const handleDelete = async (reminderId) => {
    setListError("");
    try {
      await onDeleteReminder(reminderId);
      if (form.id === reminderId) {
        resetForm();
      }
    } catch (deleteError) {
      setListError(deleteError.message || copy.notifications.errors.delete);
    }
  };

  const handleToggle = async (reminderId, enabled) => {
    setListError("");
    try {
      await onToggleReminder(reminderId, enabled);
    } catch (toggleError) {
      setListError(toggleError.message || copy.notifications.errors.toggle);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSaving(true);
    setStatus("");
    setError("");

    const payload = {
      type: "custom",
      title: form.title.trim(),
      message: form.message.trim(),
      send_time: form.send_time,
      weekdays: form.weekdays,
      send_telegram: form.channel === CHANNELS.telegram,
      send_email: form.channel === CHANNELS.email,
      enable: form.enable,
    };

    try {
      if (form.id) {
        await onUpdateReminder(form.id, payload);
        setStatus(copy.notifications.updated);
      } else {
        await onCreateReminder(payload);
        setStatus(copy.notifications.created);
      }
      resetForm();
    } catch (submitError) {
      setError(submitError.message || copy.notifications.errors.save);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-10 pb-20">
      <SectionHeader
        eyebrow={copy.notifications.eyebrow}
        title={copy.notifications.title}
        description={copy.notifications.description}
      />

      <div className="grid gap-8 xl:grid-cols-[1.05fr_1.25fr]">
        <form className="surface space-y-6 p-6" onSubmit={handleSubmit}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-diary-muted">
              {form.id ? copy.notifications.editTitle : copy.notifications.createTitle}
            </h3>
            {form.id ? (
              <button
                type="button"
                onClick={resetForm}
                className="text-xs uppercase tracking-[0.24em] text-diary-muted transition hover:text-diary-black"
              >
                {copy.notifications.reset}
              </button>
            ) : null}
          </div>

          <div className="grid gap-4">
            <input
              className="field-shell"
              name="title"
              value={form.title}
              onChange={handleFieldChange}
              placeholder={copy.notifications.fields.title}
              required
            />
            <textarea
              className="field-shell min-h-[120px] resize-none py-3"
              name="message"
              value={form.message}
              onChange={handleFieldChange}
              placeholder={copy.notifications.fields.message}
              required
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm text-diary-muted">
              <span>{copy.notifications.fields.time}</span>
              <input
                className="field-shell w-full"
                type="time"
                name="send_time"
                value={form.send_time}
                onChange={handleFieldChange}
                required
              />
            </label>

            <label className="space-y-2 text-sm text-diary-muted">
              <span>{copy.notifications.fields.channel}</span>
              <select
                className="field-shell w-full"
                name="channel"
                value={form.channel}
                onChange={handleFieldChange}
              >
                <option value={CHANNELS.telegram}>{copy.notifications.channels.telegram}</option>
                <option value={CHANNELS.email}>{copy.notifications.channels.email}</option>
              </select>
            </label>
          </div>

          <div className="space-y-3">
            <div className="text-sm text-diary-muted">{copy.notifications.fields.weekdays}</div>
            <div className="flex flex-wrap gap-2">
              {WEEKDAY_ORDER.map((weekday) => {
                const selected = form.weekdays.includes(weekday);
                return (
                  <button
                    key={weekday}
                    type="button"
                    onClick={() => handleWeekdayToggle(weekday)}
                    className={`border px-3 py-2 text-xs uppercase tracking-[0.24em] transition ${
                      selected
                        ? "border-diary-black bg-diary-black text-diary-white"
                        : "border-diary-line text-diary-muted hover:border-diary-black hover:text-diary-black"
                    }`}
                  >
                    {copy.notifications.weekdays[weekday]}
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-diary-muted">{copy.notifications.weekdaysHint}</p>
          </div>

          <label className="flex items-center gap-3 text-sm text-diary-muted">
            <input
              type="checkbox"
              name="enable"
              checked={form.enable}
              onChange={handleFieldChange}
            />
            <span>{copy.notifications.fields.enabled}</span>
          </label>

          {status ? <p className="text-sm text-emerald-700">{status}</p> : null}
          {error ? <p className="text-sm text-red-700">{error}</p> : null}

          <button
            type="submit"
            disabled={isSaving}
            className="w-full bg-diary-black py-4 text-[11px] font-semibold uppercase tracking-[0.3em] text-diary-white transition hover:bg-diary-accent disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSaving
              ? copy.notifications.saving
              : form.id
                ? copy.notifications.actions.save
                : copy.notifications.actions.create}
          </button>
        </form>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-diary-muted">
              {copy.notifications.listTitle}
            </h3>
            <span className="text-xs text-diary-muted">
              {copy.notifications.count.replace("{count}", String(sortedReminders.length))}
            </span>
          </div>

          {listError ? <p className="text-sm text-red-700">{listError}</p> : null}

          <div className="space-y-4">
            {sortedReminders.length ? (
              sortedReminders.map((reminder) => (
                <article key={reminder.id} className="surface space-y-4 p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="text-lg font-medium text-diary-black">{reminder.title}</div>
                      <div className="mt-1 text-sm text-diary-muted">{reminder.message}</div>
                    </div>
                    <span
                      className={`border px-3 py-1 text-[10px] uppercase tracking-[0.24em] ${
                        reminder.enable
                          ? "border-emerald-600 text-emerald-700"
                          : "border-diary-line text-diary-muted"
                      }`}
                    >
                      {reminder.enable ? copy.notifications.enabled : copy.notifications.disabled}
                    </span>
                  </div>

                  <div className="grid gap-3 md:grid-cols-3">
                    <div className="surface-muted px-4 py-3 text-sm text-diary-muted">
                      <div className="text-[10px] uppercase tracking-[0.24em]">{copy.notifications.fields.channel}</div>
                      <div className="mt-2 font-medium text-diary-black">
                        {reminder.send_email
                          ? copy.notifications.channels.email
                          : copy.notifications.channels.telegram}
                      </div>
                    </div>
                    <div className="surface-muted px-4 py-3 text-sm text-diary-muted">
                      <div className="text-[10px] uppercase tracking-[0.24em]">{copy.notifications.schedule}</div>
                      <div className="mt-2 font-medium text-diary-black">
                        {formatSchedule(reminder, copy)}
                      </div>
                    </div>
                    <div className="surface-muted px-4 py-3 text-sm text-diary-muted">
                      <div className="text-[10px] uppercase tracking-[0.24em]">{copy.notifications.nextSend}</div>
                      <div className="mt-2 font-medium text-diary-black">
                        {reminder.next_send_at
                          ? new Date(reminder.next_send_at).toLocaleString()
                          : copy.notifications.noNextSend}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => handleEdit(reminder)}
                      className="border border-diary-line px-4 py-2 text-xs uppercase tracking-[0.24em] transition hover:border-diary-black hover:text-diary-black"
                    >
                      {copy.notifications.actions.edit}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleToggle(reminder.id, !reminder.enable)}
                      className="border border-diary-line px-4 py-2 text-xs uppercase tracking-[0.24em] transition hover:border-diary-black hover:text-diary-black"
                    >
                      {reminder.enable
                        ? copy.notifications.actions.disable
                        : copy.notifications.actions.enable}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(reminder.id)}
                      className="border border-red-300 px-4 py-2 text-xs uppercase tracking-[0.24em] text-red-700 transition hover:bg-red-50"
                    >
                      {copy.notifications.actions.delete}
                    </button>
                  </div>
                </article>
              ))
            ) : (
              <div className="surface p-6 text-sm text-diary-muted">{copy.notifications.empty}</div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

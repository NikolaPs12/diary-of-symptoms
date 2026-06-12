export default function SectionHeader({ eyebrow, title, description, action }) {
  return (
    <div className="mb-6 flex flex-col gap-4 border-b border-diary-line pb-4 md:flex-row md:items-end md:justify-between">
      <div>
        {eyebrow ? (
          <div className="text-[11px] uppercase tracking-[0.24em] text-diary-muted">{eyebrow}</div>
        ) : null}
        <h2 className="mt-2 text-2xl font-semibold tracking-swiss md:text-3xl">{title}</h2>
        {description ? (
          <p className="mt-2 max-w-2xl text-sm leading-6 text-diary-muted">{description}</p>
        ) : null}
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}

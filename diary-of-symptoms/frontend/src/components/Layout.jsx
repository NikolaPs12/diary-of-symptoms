import { Activity, Bell, FileText, Globe, LogOut, PlusSquare, ShieldCheck, UserRound } from "lucide-react";

function formatToday(locale) {
  return new Intl.DateTimeFormat(locale === "ru" ? "ru-RU" : "en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date());
}

export default function Layout({
  route,
  onNavigate,
  currentUser,
  latestEntry,
  children,
  onLogout,
  locale,
  onToggleLocale,
  copy,
}) {
  const navItems = [
    { id: "/dashboard", label: copy.nav.dashboard, icon: Activity },
    { id: "/entry", label: copy.nav.entry, icon: PlusSquare },
    { id: "/health-state", label: copy.nav.healthState, icon: Activity },
    { id: "/notifications", label: copy.nav.notifications, icon: Bell },
    { id: "/pdf", label: copy.nav.pdf, icon: FileText },
    { id: "/profile", label: copy.nav.profile, icon: UserRound },
  ];

  return (
    <div className="min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-4 md:px-8 md:py-8">
        <header className="surface mb-6 grid gap-6 p-5 md:grid-cols-[1.1fr_1.4fr_0.9fr] md:items-start">
          <div className="space-y-4">
            <div className="text-xs uppercase tracking-[0.28em] text-diary-muted">{copy.appName}</div>
            <div>
              <h1 className="max-w-sm text-3xl font-semibold tracking-swiss md:text-5xl">
                {copy.appTitle}
              </h1>
              <p className="mt-3 max-w-md text-sm leading-6 text-diary-muted">
                {copy.appDescription}
              </p>
            </div>
          </div>

          <nav className="flex flex-wrap items-start gap-2">
            {navItems.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                type="button"
                onClick={() => onNavigate(id)}
                className={`nav-link ${route === id ? "nav-link-active" : ""}`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </nav>

          <div className="flex flex-col gap-3 md:items-end">
            <div className="surface-muted flex w-full items-center justify-between px-4 py-3 md:max-w-xs">
              <div>
                <div className="text-[11px] uppercase tracking-[0.24em] text-diary-muted">
                  {copy.header.activeUser}
                </div>
                <div className="mt-1 text-sm font-medium">{currentUser?.name ?? copy.common.guest}</div>
              </div>
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div className="flex w-full items-center justify-between text-sm text-diary-muted md:max-w-xs">
              <span>{formatToday(locale)}</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onToggleLocale}
                  className="inline-flex items-center gap-2 border border-diary-line px-3 py-2 text-diary-black transition hover:bg-diary-black hover:text-diary-white"
                >
                  <Globe className="h-4 w-4" />
                  {copy.lang}
                </button>
                <a
                  href="https://t.me/diary_of_symptoms_bot"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center border border-diary-line p-2 text-diary-black transition hover:bg-diary-black hover:text-diary-white"
                  title="Telegram bot"
                >
                  <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor">
                    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0Zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.127.037.405.02.666-.126 4.22-.6 8.338-.6 8.338s-.049.52-.302.732a.835.835 0 0 1-.535.186c-.237.005-.586-.146-.586-.146l-7.76-3.184s-.431-.181-.438-.476c0-.07.038-.183.226-.302 3.054-2.03 4.635-3.078 4.635-3.078s.408-.246.332-.546c0 0-.058-.037-.124-.027-.153.014-2.643 1.708-4.745 2.92a26.1 26.1 0 0 1-.656.4c-.414.24-.64.227-.64.227s-.44-.012-.984-.205c-.404-.143-.73-.386-.751-.408-.058-.058-.14-.185.014-.328.344-.326 2.998-1.874 4.986-2.692 1.07-.44 3.052-1.18 5.148-1.944Z" />
                  </svg>
                </a>
                <button
                  type="button"
                  onClick={onLogout}
                  className="inline-flex items-center gap-2 border border-diary-line px-3 py-2 text-diary-black transition hover:bg-diary-black hover:text-diary-white"
                >
                  <LogOut className="h-4 w-4" />
                  {copy.common.logout}
                </button>
              </div>
            </div>
            {latestEntry ? (
              <div className="surface w-full px-4 py-4 md:max-w-xs">
                <div className="text-[11px] uppercase tracking-[0.24em] text-diary-muted">
                  {copy.header.lastRecorded}
                </div>
                <div className="mt-2 font-medium">{latestEntry.symptom}</div>
                <div className="mt-1 font-mono text-sm">
                  {latestEntry.severity}/10 {copy.header.severitySuffix}
                </div>
              </div>
            ) : null}
          </div>
        </header>

        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}

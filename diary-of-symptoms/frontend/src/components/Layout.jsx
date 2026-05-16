import { Activity, Globe, LogOut, PlusSquare, ShieldCheck, UserRound } from "lucide-react";

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
    { id: "/profile", label: copy.nav.profile, icon: UserRound },
  ];

  return (
    <div className="min-h-screen">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-4 md:px-8 md:py-8">
        <header className="surface mb-6 grid gap-6 p-5 md:grid-cols-[1.1fr_1.4fr_0.9fr] md:items-start">
          <div className="space-y-4">
            <div className="text-xs uppercase tracking-[0.28em] text-codex-muted">{copy.appName}</div>
            <div>
              <h1 className="max-w-sm text-3xl font-semibold tracking-swiss md:text-5xl">
                {copy.appTitle}
              </h1>
              <p className="mt-3 max-w-md text-sm leading-6 text-codex-muted">
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
                <div className="text-[11px] uppercase tracking-[0.24em] text-codex-muted">
                  {copy.header.activeUser}
                </div>
                <div className="mt-1 text-sm font-medium">{currentUser?.name ?? copy.common.guest}</div>
              </div>
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div className="flex w-full items-center justify-between text-sm text-codex-muted md:max-w-xs">
              <span>{formatToday(locale)}</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onToggleLocale}
                  className="inline-flex items-center gap-2 border border-codex-line px-3 py-2 text-codex-black transition hover:bg-codex-black hover:text-codex-white"
                >
                  <Globe className="h-4 w-4" />
                  {copy.lang}
                </button>
                <button
                  type="button"
                  onClick={onLogout}
                  className="inline-flex items-center gap-2 border border-codex-line px-3 py-2 text-codex-black transition hover:bg-codex-black hover:text-codex-white"
                >
                  <LogOut className="h-4 w-4" />
                  {copy.common.logout}
                </button>
              </div>
            </div>
            {latestEntry ? (
              <div className="surface w-full px-4 py-4 md:max-w-xs">
                <div className="text-[11px] uppercase tracking-[0.24em] text-codex-muted">
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

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Brain, MoonStar, Siren, Sparkles } from "lucide-react";
import SectionHeader from "../components/SectionHeader";

function MetricBar({ label, value, suffix = "/10" }) {
  return (
    <div className="surface p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="text-xs uppercase tracking-[0.24em] text-diary-muted">{label}</div>
        <div className="metric-digits">
          {value}
          <span className="text-lg text-diary-muted">{suffix}</span>
        </div>
      </div>
      <div className="mt-5 h-2 w-full bg-diary-line">
        <div className="h-full bg-diary-black" style={{ width: `${Math.min(value * 10, 100)}%` }} />
      </div>
    </div>
  );
}

// ИСПРАВЛЕННЫЙ КОМПОНЕНТ: Теперь поддерживает HTML через dangerouslySetInnerHTML
function InsightQuote({ text, title }) {
  return (
    <div className="surface-muted border-l-4 border-l-diary-black p-6">
      <div className="mb-4 flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-diary-muted">
        <Brain className="h-4 w-4 text-diary-black" />
        {title}
      </div>
      {/* Заменили <p> на <div> и добавили обработку HTML */}
      <div 
        className="max-w-3xl text-base leading-8 text-diary-black ai-insight-styled"
        dangerouslySetInnerHTML={{ __html: text }} 
      />
    </div>
  );
}

export default function DashboardPage({ latestEntry, profileCard, entries, currentUser, copy }) {
  const chartData = entries.slice(0, 6).reverse().map((entry) => ({
    name: entry.symptom,
    severity: entry.severity,
    stress: entry.stress_level,
  }));

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow={copy.dashboard.eyebrow}
        title={copy.dashboard.title}
        description={copy.dashboard.description}
      />

      <section className="grid gap-6 xl:grid-cols-[1.45fr_0.95fr]">
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <MetricBar label={copy.dashboard.severity} value={latestEntry?.severity ?? 0} />
            <MetricBar label={copy.dashboard.sleepQuality} value={latestEntry?.sleep_quality ?? 0} />
            <MetricBar label={copy.dashboard.stressLevel} value={latestEntry?.stress_level ?? 0} />
          </div>

          <div className="surface p-5 md:p-6">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-[0.24em] text-diary-muted">
                  {copy.dashboard.trendMonitor}
                </div>
                <h3 className="mt-2 text-xl font-semibold tracking-swiss">
                  {copy.dashboard.recentTrend}
                </h3>
              </div>
              <div className="flex gap-3 text-xs uppercase tracking-[0.2em] text-diary-muted">
                <span className="inline-flex items-center gap-2">
                  <span className="h-2 w-2 bg-diary-black" />
                  {copy.dashboard.severity}
                </span>
                <span className="inline-flex items-center gap-2">
                  <span className="h-2 w-2 border border-diary-black bg-diary-panel" />
                  {copy.dashboard.stressLevel}
                </span>
              </div>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} barGap={10}>
                  <CartesianGrid stroke="#E5E5E5" vertical={false} />
                  <XAxis
                    dataKey="name"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: "#737373", fontSize: 12 }}
                  />
                  <YAxis
                    domain={[0, 10]}
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: "#737373", fontSize: 12 }}
                  />
                  <Tooltip
                    cursor={{ fill: "#F5F5F5" }}
                    contentStyle={{
                      borderRadius: 0,
                      border: "1px solid #000000",
                      backgroundColor: "#FFFFFF",
                    }}
                  />
                  <Bar dataKey="severity" fill="#000000" radius={0} />
                  <Bar dataKey="stress" fill="#D4D4D4" stroke="#000000" radius={0} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="surface p-5">
            <div className="mb-4 text-xs uppercase tracking-[0.24em] text-diary-muted">
              {copy.dashboard.latestEntry}
            </div>
            {latestEntry ? (
              <div className="space-y-5">
                <div>
                  <div className="text-2xl font-semibold tracking-swiss">{latestEntry.symptom}</div>
                  <div className="mt-2 text-sm leading-6 text-diary-muted">{latestEntry.notes}</div>
                </div>
                <div className="grid gap-3 border-t border-diary-line pt-5 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-2 text-diary-muted">
                      <Siren className="h-4 w-4" />
                      {copy.dashboard.severity}
                    </span>
                    <span className="font-mono">{latestEntry.severity}/10</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-2 text-diary-muted">
                      <MoonStar className="h-4 w-4" />
                      {copy.dashboard.sleepQuality}
                    </span>
                    <span className="font-mono">{latestEntry.sleep_hours}h</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-2 text-diary-muted">
                      <Sparkles className="h-4 w-4" />
                      {copy.dashboard.stressLevel}
                    </span>
                    <span className="font-mono">{latestEntry.stress_level}/10</span>
                  </div>
                  {latestEntry.body_state ? (
                    <div className="text-sm text-diary-muted">
                      <span className="text-diary-black">{copy.dashboard.bodyState}: </span>
                      {latestEntry.body_state}
                    </div>
                  ) : null}
                  {latestEntry.medications_taken ? (
                    <div className="text-sm text-diary-muted">
                      <span className="text-diary-black">{copy.dashboard.takenMedication}: </span>
                      {latestEntry.medications_taken}
                    </div>
                  ) : null}
                </div>
              </div>
            ) : (
              <p className="text-sm text-diary-muted">{copy.dashboard.noEntries}</p>
            )}
          </div>

          <div className="surface-muted p-5">
            <div className="text-xs uppercase tracking-[0.24em] text-diary-muted">{copy.dashboard.profile}</div>
            <div className="mt-4 grid gap-4">
              <div>
                <div className="text-2xl font-semibold tracking-swiss">{currentUser?.name}</div>
                <div className="mt-1 text-sm text-diary-muted">{currentUser?.email}</div>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="surface bg-transparent px-4 py-3">
                  <div className="text-diary-muted">{copy.dashboard.plan}</div>
                  <div className="mt-1 font-mono uppercase text-diary-black">
                    {currentUser?.plan_type ?? "free"}
                  </div>
                </div>
                <div className="surface bg-transparent px-4 py-3">
                  <div className="text-diary-muted">{copy.dashboard.profileCard}</div>
                  <div className="mt-1 font-mono text-diary-black">{profileCard ? "01" : "00"}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {latestEntry?.ai_insights ? (
        <InsightQuote text={latestEntry.ai_insights} title={copy.dashboard.aiInsights} />
      ) : null}

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="surface p-5">
          <div className="mb-4 text-xs uppercase tracking-[0.24em] text-diary-muted">
            {copy.dashboard.recentEntries}
          </div>
          <div className="space-y-3">
            {entries.slice(0, 4).map((entry) => (
              <div
                key={entry.id}
                className="grid gap-2 border-b border-diary-line pb-3 last:border-b-0 last:pb-0 md:grid-cols-[1.1fr_0.55fr_0.55fr]"
              >
                <div>
                  <div className="font-medium">{entry.symptom}</div>
                  <div className="mt-1 text-sm text-diary-muted">
                    {entry.duration} {copy.dashboard.duration}
                  </div>
                </div>
                <div className="font-mono text-sm">{entry.severity}/10</div>
                <div className="font-mono text-sm">{entry.stress_level}/10 {copy.dashboard.stress}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="surface p-5">
          <div className="mb-4 text-xs uppercase tracking-[0.24em] text-diary-muted">
            {copy.dashboard.cardSummary}
          </div>
          {profileCard ? (
            <div className="grid gap-3 text-sm">
              <div className="surface-muted p-4">
                <div className="text-diary-muted">{copy.card.medication}</div>
                <div className="mt-1 font-medium">{profileCard.name}</div>
              </div>
              <div className="surface-muted p-4">
                <div className="text-diary-muted">{copy.card.dosage}</div>
                <div className="mt-1 font-mono">{profileCard.dosage}</div>
              </div>
              <div className="surface-muted p-4">
                <div className="text-diary-muted">{copy.card.diagnosis}</div>
                <div className="mt-1">{profileCard.diagnosis}</div>
              </div>
              <div className="surface-muted p-4">
                <div className="text-diary-muted">{copy.card.allergies}</div>
                <div className="mt-1">
                  {profileCard.allergies?.length
                    ? profileCard.allergies.join(", ")
                    : copy.common.noneListed}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-sm text-diary-muted">{copy.profile.noCard}</p>
          )}
        </div>
      </section>
    </div>
  );
}
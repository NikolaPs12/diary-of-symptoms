import { useEffect, useMemo, useState } from "react";
import Layout from "./components/Layout";
import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";
import HealthStatePage from "./pages/HealthStatePage";
import PdfExportPage from "./pages/PdfExportPage";
import ProfilePage from "./pages/ProfilePage";
import SymptomEntryPage from "./pages/SymptomEntryPage";
import {
  createSymptomEntry,
  exportPdfReport,
  getAppSnapshot,
  loginUser,
  logoutUser,
  registerUser,
  saveProfileCard,
} from "./lib/api";
import { getTranslation } from "./lib/translations";

const DEFAULT_ROUTE = "/dashboard";
const AUTH_ROUTES = ["/login", "/register"];

function getRouteFromHash() {
  const rawHash = window.location.hash.replace("#", "") || DEFAULT_ROUTE;
  return rawHash.startsWith("/") ? rawHash : DEFAULT_ROUTE;
}

function navigateTo(route) {
  window.location.hash = route;
}

function getInitialLocale() {
  return "en";
}

function formatDate(date) {
  return date.toISOString().slice(0, 10);
}

function loadForms(locale) {
  return {
    login: {
      email: "nikola@diary.health",
      password: "demo12345",
      locale,
    },
    register: {
      name: "",
      email: "",
      password: "",
      age: "",
      weight: "",
      height: "",
      puls_is_normal: "",
      pressure_is_normal: "",
      medication_name: "",
      dosage: "",
      diagnosis: "",
      allergies: "",
      medication_notes: "",
      locale,
    },
  };
}

export default function App() {
  const [route, setRoute] = useState(
    typeof window === "undefined" ? DEFAULT_ROUTE : getRouteFromHash(),
  );
  const [snapshot, setSnapshot] = useState({
    currentUser: null,
    entries: [],
    latestEntry: null,
    healthScores: [],
    medications: [],
    profileCard: null,
  });
  const [locale, setLocale] = useState(getInitialLocale);
  const [authForms, setAuthForms] = useState(() => loadForms(getInitialLocale()));
  const [authError, setAuthError] = useState("");
  const [pdfRange, setPdfRange] = useState({ startDate: "", endDate: "" });
  const [pdfStatus, setPdfStatus] = useState("");
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  const copy = getTranslation(locale);

  const refreshSnapshot = async () => {
    setSnapshot(await getAppSnapshot());
  };

  const handlePdfExport = async (exporter) => {
    try {
      const filename = await exporter();
      setPdfStatus(copy.pdf.statusReady.replace("{file}", filename));
    } catch (error) {
      setPdfStatus(error.message || copy.pdf.statusError);
    }
  };

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(getRouteFromHash());
    };

    if (!window.location.hash) {
      navigateTo(snapshot.currentUser ? DEFAULT_ROUTE : "/login");
    }

    refreshSnapshot().finally(() => setIsBootstrapping(false));
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    if (!isBootstrapping && !snapshot.currentUser && !AUTH_ROUTES.includes(route)) {
      navigateTo("/login");
    }
  }, [isBootstrapping, route, snapshot.currentUser]);

  useEffect(() => {
    setAuthForms((current) => ({
      login: { ...current.login, locale },
      register: { ...current.register, locale },
    }));
  }, [locale]);

  const currentMode = route === "/register" ? "register" : "login";
  const currentAuthForm = authForms[currentMode];

  const pageContent = useMemo(() => {
    switch (route) {
      case "/entry":
        return (
          <SymptomEntryPage
            copy={copy}
            onSubmitEntry={async (form) => {
              const nextEntry = await createSymptomEntry(form);
              await refreshSnapshot();
              return nextEntry;
            }}
          />
        );
      case "/health-state":
        return (
          <HealthStatePage
            copy={copy}
            onSubmitEntry={async (form) => {
              const nextEntry = await createSymptomEntry(form);
              await refreshSnapshot();
              return nextEntry;
            }}
          />
        );
      case "/profile":
        return (
          <ProfilePage
            currentUser={snapshot.currentUser}
            profileCard={snapshot.profileCard}
            copy={copy}
            onSaveProfileCard={async (form) => {
              await saveProfileCard(form);
              await refreshSnapshot();
            }}
          />
        );
      case "/pdf":
        return (
          <PdfExportPage
            copy={copy}
            startDate={pdfRange.startDate}
            endDate={pdfRange.endDate}
            onDateChange={(event) => {
              const { name, value } = event.target;
              setPdfRange((current) => ({ ...current, [name]: value }));
              setPdfStatus("");
            }}
            onExportRange={async () => {
              if (!pdfRange.startDate && !pdfRange.endDate) {
                setPdfStatus(copy.pdf.statusMissing);
                return;
              }

              await handlePdfExport(() =>
                exportPdfReport({
                  startDate: pdfRange.startDate,
                  endDate: pdfRange.endDate,
                }),
              );
            }}
            onExportWeek={async () => {
              const end = new Date();
              const start = new Date();
              start.setDate(end.getDate() - 7);

              const nextRange = {
                startDate: formatDate(start),
                endDate: formatDate(end),
              };

              setPdfRange(nextRange);
              await handlePdfExport(() => exportPdfReport(nextRange));
            }}
            onExportMonth={async () => {
              const end = new Date();
              const start = new Date();
              start.setMonth(end.getMonth() - 1);

              const nextRange = {
                startDate: formatDate(start),
                endDate: formatDate(end),
              };

              setPdfRange(nextRange);
              await handlePdfExport(() => exportPdfReport(nextRange));
            }}
            onExportAll={async () => {
              await handlePdfExport(() => exportPdfReport({ includeAll: true }));
            }}
            status={pdfStatus}
          />
        );
      case "/dashboard":
      default:
        return (
          <DashboardPage
            latestEntry={snapshot.latestEntry}
            profileCard={snapshot.profileCard}
            entries={snapshot.entries}
            currentUser={snapshot.currentUser}
            healthScores={snapshot.healthScores}
            copy={copy}
          />
        );
    }
  }, [route, snapshot, copy, pdfRange, pdfStatus]);

  const handleAuthFieldChange = (event) => {
    const { name, value } = event.target;
    setAuthForms((current) => ({
      ...current,
      [currentMode]: {
        ...current[currentMode],
        [name]: value,
      },
    }));
  };

  const handleAuthSubmit = async (event) => {
    event.preventDefault();
    setAuthError("");

    try {
      if (currentMode === "register") {
        await registerUser(currentAuthForm);
      } else {
        await loginUser(currentAuthForm);
      }
      await refreshSnapshot();
      navigateTo(DEFAULT_ROUTE);
    } catch (error) {
      setAuthError(error.message || "Unable to continue");
    }
  };

  const handleLogout = () => {
    logoutUser();
    setSnapshot({
      currentUser: null,
      entries: [],
      latestEntry: null,
      healthScores: [],
      medications: [],
      profileCard: null,
    });
    navigateTo("/login");
  };

  const handleToggleLocale = () => {
    setLocale((current) => (current === "ru" ? "en" : "ru"));
  };

  if (isBootstrapping) {
    return null;
  }

  if (!snapshot.currentUser || AUTH_ROUTES.includes(route)) {
    return (
      <AuthPage
        mode={currentMode}
        form={currentAuthForm}
        onChange={handleAuthFieldChange}
        onSubmit={handleAuthSubmit}
        onSwitchMode={() => {
          setAuthError("");
          navigateTo(currentMode === "register" ? "/login" : "/register");
        }}
        error={authError}
        copy={copy}
        locale={locale}
        onToggleLocale={handleToggleLocale}
      />
    );
  }

  return (
    <Layout
      route={route}
      onNavigate={navigateTo}
      currentUser={snapshot.currentUser}
      latestEntry={snapshot.latestEntry}
      onLogout={handleLogout}
      locale={locale}
      onToggleLocale={handleToggleLocale}
      copy={copy}
    >
      {pageContent}
    </Layout>
  );
}

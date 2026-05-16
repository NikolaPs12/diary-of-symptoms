import { useEffect, useMemo, useState } from "react";
import Layout from "./components/Layout";
import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";
import ProfilePage from "./pages/ProfilePage";
import SymptomEntryPage from "./pages/SymptomEntryPage";
import {
  createSymptomEntry,
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

function loadForms(locale) {
  return {
    login: {
      email: "nikola@codex.health",
      password: "demo12345",
      name: "",
      weight: "",
      height: "",
      medication_name: "",
      dosage: "",
      diagnosis: "",
      allergies: "",
      medication_notes: "",
      locale,
    },
    register: {
      name: "",
      email: "",
      password: "",
      weight: "",
      height: "",
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
    medications: [],
    profileCard: null,
  });
  const [locale, setLocale] = useState(getInitialLocale);
  const [authForms, setAuthForms] = useState(() => loadForms(getInitialLocale()));
  const [authError, setAuthError] = useState("");

  const copy = getTranslation(locale);

  const refreshSnapshot = async () => {
    setSnapshot(await getAppSnapshot());
  };

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(getRouteFromHash());
    };

    if (!window.location.hash) {
      navigateTo(snapshot.currentUser ? DEFAULT_ROUTE : "/login");
    }

    void refreshSnapshot();
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    if (!snapshot.currentUser && !AUTH_ROUTES.includes(route)) {
      navigateTo("/login");
    }
  }, [route, snapshot.currentUser]);

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
      case "/dashboard":
      default:
        return (
          <DashboardPage
            latestEntry={snapshot.latestEntry}
            profileCard={snapshot.profileCard}
            entries={snapshot.entries}
            currentUser={snapshot.currentUser}
            copy={copy}
          />
        );
    }
  }, [route, snapshot, copy]);

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
      medications: [],
      profileCard: null,
    });
    navigateTo("/login");
  };

  const handleToggleLocale = () => {
    setLocale((current) => (current === "ru" ? "en" : "ru"));
  };

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

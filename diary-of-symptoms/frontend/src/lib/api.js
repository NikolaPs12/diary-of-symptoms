// Force all requests to the local backend. In this setup the only valid backend
// host is localhost:8000, so we hardcode it to avoid any accidental external
// routing when the app is exposed via a tunnel.
const API_BASE = "http://localhost:8000";

// Runtime debug: print forced API base and current hostname in browser console
if (typeof window !== "undefined") {
  try {
    // eslint-disable-next-line no-console
    console.debug("[api] FORCED API_BASE:", API_BASE, "hostname:", window.location.hostname);
  } catch (e) {
    // ignore
  }
}
const AUTH_STORAGE_KEY = "diary.auth";

let currentUser = null;
let authToken = null;

function loadAuthSession() {
  if (typeof window === "undefined") {
    return;
  }

  try {
    const rawSession = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!rawSession) {
      return;
    }

    const session = JSON.parse(rawSession);
    currentUser = session.user?.id ? session.user : null;
    authToken = session.token ?? null;
  } catch {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    currentUser = null;
    authToken = null;
  }
}

function saveAuthSession({ user, token }) {
  currentUser = user?.id ? user : null;
  authToken = token ?? null;

  if (typeof window !== "undefined") {
    if (currentUser) {
      window.localStorage.setItem(
        AUTH_STORAGE_KEY,
        JSON.stringify({ user: currentUser, token: authToken }),
      );
    } else {
      window.localStorage.removeItem(AUTH_STORAGE_KEY);
    }
  }

  return currentUser;
}

function clearAuthSession() {
  currentUser = null;
  authToken = null;

  if (typeof window !== "undefined") {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
  }
}

function normalizeAuthResponse(response) {
  const user = response?.user ?? response;
  const token = response?.token ?? response?.access_token ?? null;

  if (!user?.id) {
    throw new Error("Login response does not include a user id");
  }

  return { user, token };
}

loadAuthSession();

function buildQuery(params) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });

  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

function normalizeEntry(entry) {
  return {
    id: entry.id ?? Date.now(),
    symptom: entry.symptom ?? "Unknown symptom",
    severity: Number(entry.severity ?? 0),
    duration: String(entry.duration ?? "0h"),
    start_at: entry.start_at ?? new Date().toISOString(),
    body_state: entry.body_state ?? "",
    sleep_quality: Number(entry.sleep_quality ?? entry.sleepQuality ?? 0),
    sleep_hours: Number(entry.sleep_hours ?? entry.sleepHours ?? 0),
    stress_level: Number(entry.stress_level ?? entry.stressLevel ?? 0),
    notes: entry.notes ?? "",
    food_notes: entry.food_notes ?? entry.foodNotes ?? "",
    medications_taken: entry.medications_taken ?? entry.medicationsTaken ?? "",
    ai_insights: entry.ai_insights ?? entry.aiInsights ?? "",
    created_at: entry.created_at ?? new Date().toISOString(),
  };
}

function normalizeMedication(medication) {
  const regularList = medication.regular_medications ?? medication.regularMedication ?? [];
  return {
    id: medication.id ?? Date.now(),
    name:
      medication.name ??
      regularList[0] ??
      medication.regular_medications_dosage ??
      "Medication",
    dosage: medication.dosage ?? medication.regular_medications_dosage ?? "Not specified",
    diagnosis: medication.diagnosis ?? "Unspecified",
    notes: medication.notes ?? "",
    regular_medications: Array.isArray(regularList) ? regularList : [regularList].filter(Boolean),
    allergies: medication.allergies ?? medication.allergy ?? [],
    puls_is_normal: medication.puls_is_normal ?? medication.pulse ?? null,
    pressure_is_normal: medication.pressure_is_normal ?? medication.pressure ?? null,
    created_at: medication.created_at ?? new Date().toISOString(),
  };
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = "Request failed";

    try {
      const errorBody = await response.json();
      message = errorBody.detail ?? JSON.stringify(errorBody);
    } catch {
      message = await response.text();
    }

    throw new Error(message || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

async function requestBlob(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = "Request failed";

    try {
      const errorBody = await response.json();
      message = errorBody.detail ?? JSON.stringify(errorBody);
    } catch {
      message = await response.text();
    }

    throw new Error(message || "Request failed");
  }

  const blob = await response.blob();
  const contentDisposition = response.headers.get("Content-Disposition") ?? "";
  const filenameMatch = contentDisposition.match(/filename=\"([^\"]+)\"/);

  return {
    blob,
    filename: filenameMatch?.[1] ?? "symptoms_report.pdf",
  };
}

export async function getAppSnapshot() {
  if (!currentUser?.id) {
    return {
      currentUser: null,
      entries: [],
      latestEntry: null,
      healthScores: [],
      medications: [],
      profileCard: null,
    };
  }

  const [freshUser, entriesResponse, medicationsResponse, healthScores] = await Promise.all([
    request(`/api/users/${currentUser.id}`),
    request(`/api/symptom-entries?user_id=${currentUser.id}`),
    request(`/api/medications?user_id=${currentUser.id}`),
    getHealthScores(),
  ]);

  saveAuthSession({ user: freshUser, token: authToken });

  const entries = entriesResponse
    .map(normalizeEntry)
    .sort((first, second) => new Date(second.created_at) - new Date(first.created_at));
  const medications = medicationsResponse
    .map(normalizeMedication)
    .sort((first, second) => new Date(second.created_at) - new Date(first.created_at));

  return {
    currentUser: freshUser,
    entries,
    latestEntry: entries[0] ?? null,
    healthScores,
    medications,
    profileCard: medications[0] ?? null,
  };
}

export async function getHealthScores() {
  if (!currentUser?.id) return [];
  const scores = await request(`/api/health-scores?user_id=${currentUser.id}`);
  return (scores || []).map((score) => ({
    id: score.id,
    user_id: score.user_id,
    score: Number(score.score),
    calculated_at: score.calculated_at ?? score.сalculated_at,
  }));
}

export async function loginUser({ email, password }) {
  try {
    const response = await request("/api/users/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    const session = normalizeAuthResponse(response);
    return saveAuthSession(session);
  } catch {
    throw new Error("Invalid email or password");
  }
}

export async function registerUser(formData) {
  const userPayload = {
    name: formData.name,
    email: formData.email,
    password: formData.password,
    plan_type: "free",
    age: Number(formData.age) || null,
    weight: Number(formData.weight) || null,
    height: Number(formData.height) || null,
    puls_is_normal: Number(formData.puls_is_normal) || null,
    pressure_is_normal: formData.pressure_is_normal || null,
    locale: formData.locale ?? "en",
  };

  try {
    const response = await request("/api/users/register", {
      method: "POST",
      body: JSON.stringify(userPayload),
    });
    const session = normalizeAuthResponse(response);
    saveAuthSession(session);
  } catch (error) {
    if (error.message.includes("Email already registered")) {
      throw new Error("This email is already registered");
    }
    throw error;
  }

  if (formData.medication_name) {
    await request("/api/medications/add", {
      method: "POST",
      body: JSON.stringify({
        name: formData.medication_name,
        dosage: formData.dosage,
        diagnosis: formData.diagnosis,
        notes: formData.medication_notes,
        regular_medications: [formData.medication_name],
        allergies: formData.allergies
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        user_id: currentUser.id,
      }),
    });
  }

  return currentUser;
}

export function logoutUser() {
  clearAuthSession();
}

export async function createSymptomEntry(formData) {
  const remoteEntry = await request("/api/symptom-entries/add", {
    method: "POST",
    body: JSON.stringify({
      symptom: formData.symptom,
      severity: Number(formData.severity),
      duration: formData.duration,
      start_at: formData.start_at,
      body_state: formData.body_state,
      sleep_quality: Number(formData.sleep_quality),
      sleep_hours: Number(formData.sleep_hours),
      stress_level: Number(formData.stress_level),
      notes: formData.notes,
      food_notes: formData.food_notes,
      medications_taken: formData.medications_taken,
      user_id: currentUser?.id ?? null,
    }),
  });

  return normalizeEntry(remoteEntry);
}

export async function saveProfileCard(formData) {
  if (!currentUser?.id) {
    throw new Error("User is not authenticated");
  }

  currentUser = await request(`/api/users/${currentUser.id}`, {
    method: "PUT",
    body: JSON.stringify({
      name: formData.name || currentUser.name,
      weight: Number(formData.weight) || null,
      height: Number(formData.height) || null,
      puls_is_normal: Number(formData.puls_is_normal) || null,
      pressure_is_normal: formData.pressure_is_normal || null,
    }),
  });

  if (!formData.medication_name) {
    return null;
  }

  const medication = await request("/api/medications/add", {
    method: "POST",
    body: JSON.stringify({
      name: formData.medication_name,
      dosage: formData.dosage,
      diagnosis: formData.diagnosis,
      notes: formData.notes,
      regular_medications: [formData.medication_name],
      allergies: Array.isArray(formData.allergies) ? formData.allergies : [],
      user_id: currentUser.id,
    }),
  });

  return normalizeMedication(medication);
}

export async function exportPdfReport({ startDate, endDate, includeAll = false }) {
  if (!currentUser?.id) {
    throw new Error("User is not authenticated");
  }

  const query = includeAll
    ? buildQuery({ user_id: currentUser.id })
    : buildQuery({
        start_date: startDate,
        end_date: endDate,
        user_id: currentUser.id,
      });

  const { blob, filename } = await requestBlob(`/api/generation/pdf${query}`);
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);

  return filename;
}

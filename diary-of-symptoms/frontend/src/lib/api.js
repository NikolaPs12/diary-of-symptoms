const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
let currentUser = null;

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

export async function getAppSnapshot() {
  if (!currentUser?.id) {
    return {
      currentUser: null,
      entries: [],
      latestEntry: null,
      medications: [],
      profileCard: null,
    };
  }

  const [freshUser, entriesResponse, medicationsResponse] = await Promise.all([
    request(`/api/users/${currentUser.id}`),
    request(`/api/symptom-entries?user_id=${currentUser.id}`),
    request(`/api/medications?user_id=${currentUser.id}`),
  ]);

  currentUser = freshUser;

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
    medications,
    profileCard: medications[0] ?? null,
  };
}

export async function loginUser({ email, password }) {
  try {
    currentUser = await request("/api/users/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    return currentUser;
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
    weight: Number(formData.weight) || null,
    height: Number(formData.height) || null,
    puls_is_normal: Number(formData.puls_is_normal) || null,
    pressure_is_normal: formData.pressure_is_normal || null,
    locale: formData.locale ?? "en",
  };

  try {
    currentUser = await request("/api/users/register", {
      method: "POST",
      body: JSON.stringify(userPayload),
    });
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
  currentUser = null;
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

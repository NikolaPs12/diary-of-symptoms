export const THEME_STORAGE_KEY = "theme";
export const DEFAULT_THEME = "classic";

export const themeDefinitions = {
  classic: {
    id: "classic",
    name: "Classic Clinical",
    description: "Минималистичный клинический интерфейс с тонкими границами и максимальной читаемостью.",
    idea: "Apple Health × Linear",
    whenToUse: "Для повседневной работы и как основной профессиональный режим.",
  },
  midnight: {
    id: "midnight",
    name: "Midnight Health",
    description: "Спокойный ночной режим для долгих сессий, снижает зрительное напряжение.",
    idea: "GitHub Dark × Arc Browser",
    whenToUse: "Для вечернего мониторинга и работы при слабом освещении.",
  },
  medical: {
    id: "medical",
    name: "Medical Dashboard",
    description: "Холодная структурная тема с ощущением надёжной медицинской системы.",
    idea: "Epic Systems × modern SaaS",
    whenToUse: "Для аналитики, графиков и рабочего режима с акцентом на структуру.",
  },
  focus: {
    id: "focus",
    name: "Focus Mode",
    description: "Мягкий дневниковый режим с меньшим визуальным шумом и paper-like поверхностями.",
    idea: "Notion × paper notebook",
    whenToUse: "Для спокойного заполнения записей и личных рефлексивных сессий.",
  },
  glass: {
    id: "glass",
    name: "Glass Health",
    description: "Премиальный стеклянный режим с прозрачностью и лёгкой глубиной.",
    idea: "Apple VisionOS",
    whenToUse: "Для современного презентационного вида без потери медицинской строгости.",
  },
};

export const themeOrder = ["classic", "midnight", "medical", "focus", "glass"];

export function isThemeId(value) {
  return typeof value === "string" && Object.prototype.hasOwnProperty.call(themeDefinitions, value);
}

export function getStoredTheme() {
  if (typeof window === "undefined") {
    return DEFAULT_THEME;
  }

  const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
  return isThemeId(storedTheme) ? storedTheme : DEFAULT_THEME;
}

export function applyTheme(themeId) {
  const nextTheme = isThemeId(themeId) ? themeId : DEFAULT_THEME;

  if (typeof document !== "undefined") {
    document.documentElement.dataset.theme = nextTheme;
  }

  if (typeof window !== "undefined") {
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  }

  return nextTheme;
}

export function initializeTheme() {
  return applyTheme(getStoredTheme());
}

export function buildThemePreview(themeId) {
  const previewMap = {
    classic: {
      background: "linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)",
      surface: "#ffffff",
      accent: "#4f46e5",
      text: "#111111",
      border: "#d6d6d6",
    },
    midnight: {
      background: "linear-gradient(135deg, #0d1320 0%, #111827 100%)",
      surface: "rgba(23, 32, 51, 0.88)",
      accent: "#7dd3fc",
      text: "#ecf2ff",
      border: "rgba(148, 163, 184, 0.24)",
    },
    medical: {
      background: "linear-gradient(135deg, #eef6fb 0%, #ddeaf5 100%)",
      surface: "#f8fbfd",
      accent: "#2563eb",
      text: "#13324a",
      border: "#bfd5e6",
    },
    focus: {
      background: "linear-gradient(135deg, #fbf7ef 0%, #f4ede1 100%)",
      surface: "#fffdf8",
      accent: "#7c5c35",
      text: "#2f2418",
      border: "#ddd0bf",
    },
    glass: {
      background: "linear-gradient(135deg, #edf5ff 0%, #dce8ff 50%, #f5f9ff 100%)",
      surface: "rgba(255, 255, 255, 0.50)",
      accent: "#2563eb",
      text: "#0f172a",
      border: "rgba(255, 255, 255, 0.66)",
    },
  };

  return previewMap[themeId] ?? previewMap[DEFAULT_THEME];
}

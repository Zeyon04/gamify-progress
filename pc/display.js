// pc/display.js (versión sin recargas automáticas)
const DATA_PATH = "../data/data.json";

const BASE_XP = {
  estudiar: 1.0,
  lectura: 0.25,
  entrenar: 1.0,
  andar: 0.25,
  meditar: 1.0,
  organizar: 1.0,
};

let state = null;
let weeklyChart = null;
let dataLoaded = false; // evita recargar varias veces

// ----------------- util -----------------
function formatDateDDMMFromISO(iso) {
  if (!iso) return "";
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}
function isoDate(dateObj) {
  return dateObj.toISOString().split("T")[0];
}
function levelXpRequired(level) {
  return Math.round(50 * Math.pow(1.01, Math.max(1, level) - 1));
}
function lastNDates(n) {
  const arr = [];
  const today = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    arr.push(isoDate(d));
  }
  return arr;
}
function weekdayLetterFromISO(iso) {
  const d = new Date(iso + "T00:00:00");
  const map = ["D", "L", "M", "X", "J", "V", "S"];
  return map[d.getDay()];
}

// ----------------- carga -----------------
async function loadData() {
  if (dataLoaded) return;
  dataLoaded = true;

  try {
    const res = await fetch(DATA_PATH, { cache: "no-store" });
    if (!res.ok) throw new Error("No se pudo leer data.json: " + res.status);
    state = await res.json();
  } catch (err) {
    console.error("Error al cargar data.json:", err);
    state = {
      areas: {},
      last_processed_date: isoDate(new Date()),
      food_log: {},
      sleep_log: {},
    };
  }

  renderAll();
}

// ----------------- render principal -----------------
function renderAll() {
  renderDate();
  renderTodaySummary();
  renderLevels();
  renderWeeklyChart();
}

function renderDate() {
  const iso =
    (state && state.last_processed_date)
      ? state.last_processed_date
      : isoDate(new Date());
  const el = document.getElementById("bigDate");
  if (el) el.textContent = formatDateDDMMFromISO(iso);
}

// ----------------- panel izquierdo -----------------
function setIfExists(ids, text) {
  for (const id of ids) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = text;
      return true;
    }
  }
  return false;
}

function renderTodaySummary() {
  const dateToShow =
    (state && state.last_processed_date)
      ? state.last_processed_date
      : isoDate(new Date());
  const areas = state.areas || {};

  let totalMinutes = 0;
  const tasks = {
    entrenar: 0,
    andar: 0,
    estudiar: 0,
    meditar: 0,
    organizar: 0,
    lectura: 0,
  };

  Object.keys(areas).forEach((area) => {
    const a = areas[area] || {};
    const sessions = (a.sessions && a.sessions[dateToShow]) || {};
    for (const t in sessions) {
      const mins = Number(sessions[t] || 0);
      totalMinutes += mins;
      if (tasks.hasOwnProperty(t)) tasks[t] += mins;
    }
  });

  setIfExists(["minutesToday", "minutes_today", "minutes"], `${totalMinutes} min`);
  setIfExists(["m_entrenar", "min_entrenar"], `${tasks.entrenar} min`);
  setIfExists(["m_andar", "min_andar"], `${tasks.andar} min`);
  setIfExists(["m_estudiar", "min_estudiar"], `${tasks.estudiar} min`);
  setIfExists(["m_meditar", "min_meditar"], `${tasks.meditar} min`);
  setIfExists(["m_organizar", "min_organizar"], `${tasks.organizar} min`);
  setIfExists(["m_lectura", "min_lectura"], `${tasks.lectura} min`);

  // COMIDAS
  const foodOk = !!((state.food_log || {})[dateToShow]);
  setIfExists(["comidas_ok", "food_ok", "comidas", "food"], foodOk ? "SI" : "NO");

  // DORMIR
  const sleepOk = !!((state.sleep_log || {})[dateToShow]);
  setIfExists(["dormir_ok", "sleep_ok", "dormir", "sleep"], sleepOk ? "SI" : "NO");
}

// ----------------- niveles -----------------
function ensureAreaDefaults(areaKey) {
  const a = state.areas[areaKey];
  if (!a)
    state.areas[areaKey] = { xp: 0, level: 1, rate: 1.0, sessions: {} };
  else {
    a.xp = a.xp || 0;
    a.level = a.level || 1;
    a.rate = typeof a.rate === "number" ? a.rate : 1.0;
    a.sessions = a.sessions || {};
  }
}

function renderLevels() {
  const order = ["inteligencia", "ejercicio", "salud_mental"];
  order.forEach((k) => ensureAreaDefaults(k));

  order.forEach((areaKey) => {
    const area = state.areas[areaKey];
    const lvlEl = document.getElementById(`lvl_${areaKey}`);
    const expEl = document.getElementById(`exp_${areaKey}`);
    const rateEl = document.getElementById(`rate_${areaKey}`);
    const fillEl = document.querySelector(
      `.xp-row[data-area="${areaKey}"] .xp-fill`
    );

    const req = levelXpRequired(area.level);
    const curXP = Number(area.xp || 0);
    const percent = Math.min(100, Math.round((curXP / req) * 100));

    if (lvlEl) lvlEl.textContent = `Lvl. ${area.level}`;
    if (expEl) expEl.textContent = `${curXP} / ${req}`;
    if (rateEl) rateEl.textContent = `Rate: ${Math.round(area.rate * 100)}%`;
    if (fillEl) fillEl.style.width = `${percent}%`;
  });
}

// ----------------- gráfico -----------------
function computeDailyXPForArea(areaKey, isoDateStr) {
  const area = state.areas[areaKey] || { sessions: {} };
  const tasks = (area.sessions && area.sessions[isoDateStr]) || {};
  let xp = 0;
  for (const t in tasks) xp += (BASE_XP[t] || 0) * Number(tasks[t] || 0);
  return xp;
}

function renderWeeklyChart() {
  const labelsISO = lastNDates(7);
  const labels = labelsISO.map((d) => weekdayLetterFromISO(d));

  const dataIntel = labelsISO.map((d) =>
    computeDailyXPForArea("inteligencia", d)
  );
  const dataEjerc = labelsISO.map((d) =>
    computeDailyXPForArea("ejercicio", d)
  );
  const dataMental = labelsISO.map((d) =>
    computeDailyXPForArea("salud_mental", d)
  );

  const canvas = document.getElementById("weeklyChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  if (weeklyChart) weeklyChart.destroy();

  weeklyChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Inteligencia", data: dataIntel, backgroundColor: "#ff9e2a" },
        { label: "Ejercicio", data: dataEjerc, backgroundColor: "#d14cff" },
        { label: "Salud Mental", data: dataMental, backgroundColor: "#6b00d4" },
      ],
    },
    options: {
      animation: false,
      responsive: false,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#dcdcdc" } },
        y: { beginAtZero: true, ticks: { color: "#dcdcdc" } },
      },
    },
  });
}

// ----------------- inicio -----------------
window.addEventListener("DOMContentLoaded", loadData);

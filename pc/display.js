// display.js

// --- Configuración ---
const DATA_PATH = "../data/data.json";  // ruta relativa a pc/

let dailyMode = true;  // modo inicial: diario
let dataState = null;

// --- Funciones de carga ---
async function loadData() {
  try {
    const response = await fetch(DATA_PATH);
    dataState = await response.json();
    updateDisplay();
  } catch (err) {
    console.error("Error cargando data.json:", err);
  }
}

// --- Helpers ---
function createBar(container, label, value, max=100) {
  const barContainer = document.createElement("div");
  barContainer.className = "bar-container";

  const barLabel = document.createElement("div");
  barLabel.className = "bar-label";
  barLabel.textContent = label;

  const bar = document.createElement("div");
  bar.className = "bar";
  bar.style.width = `${Math.min(value / max * 100, 100)}%`;

  barContainer.appendChild(barLabel);
  barContainer.appendChild(bar);
  container.appendChild(barContainer);
}

// --- Update display ---
function updateDisplay() {
  const titleEl = document.getElementById("display-title");
  titleEl.textContent = "OSCAR";

  // Minutos acumulados hoy
  const today = new Date().toISOString().split("T")[0];
  let todayMinutes = 0;
  for (const area in dataState.areas) {
    const dayTasks = dataState.areas[area].sessions[today] || {};
    for (const task in dayTasks) {
      todayMinutes += dayTasks[task];
    }
  }
  document.getElementById("today-minutes").textContent = todayMinutes + " min";

  // Barras de experiencia por área
  const expContainer = document.getElementById("exp-bars");
  expContainer.innerHTML = "";
  for (const area in dataState.areas) {
    const areaData = dataState.areas[area];
    createBar(expContainer, area, areaData.xp, 100);
  }

  // Gráfico de experiencia diario/mensual
  drawExpChart();
}

// --- Gráfico ---
function drawExpChart() {
  const canvas = document.getElementById("exp-chart");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0,0,canvas.width,canvas.height);

  // Preparar datos
  const days = dailyMode ? 7 : 4;  // últimas 7 días o 4 meses aprox.
  const labels = [];
  const totals = [];

  const areaNames = Object.keys(dataState.areas);
  const allDates = Object.values(dataState.areas[areaNames[0]].sessions).length > 0 ?
                   Object.keys(dataState.areas[areaNames[0]].sessions) : [];

  // Recogemos últimos días
  let lastDates = allDates.slice(-days);

  lastDates.forEach(date => {
    labels.push(date);
    let totalXP = 0;
    areaNames.forEach(area => {
      const dayTasks = dataState.areas[area].sessions[date] || {};
      for (const t in dayTasks) {
        totalXP += dayTasks[t];
      }
    });
    totals.push(totalXP);
  });

  // Dibujar barras
  const barWidth = canvas.width / totals.length * 0.6;
  const maxXP = Math.max(...totals, 1);

  totals.forEach((val, i) => {
    const x = i * (canvas.width / totals.length) + (canvas.width / totals.length - barWidth)/2;
    const y = canvas.height - (val / maxXP * canvas.height);
    const height = canvas.height - y;
    ctx.fillStyle = "#FFD700"; // dorado para barras
    ctx.fillRect(x, y, barWidth, height);

    // Texto
    ctx.fillStyle = "#FFF";
    ctx.font = "12px 'Comic Sans MS', cursive, sans-serif";
    ctx.fillText(val, x + barWidth/4, y - 5);
  });
}

// --- Toggle diario/mensual ---
document.getElementById("toggle-chart").addEventListener("click", () => {
  dailyMode = !dailyMode;
  drawExpChart();
});

// --- Inicialización ---
window.onload = loadData;

// Leer data.json
fetch('../data/data.json')
  .then(res => res.json())
  .then(data => {
    updateDisplay(data);
  });

function updateDisplay(data) {
  // Minutos acumulados hoy
  const today = new Date().toISOString().slice(0,10);
  let minutesToday = 0;
  for (let area in data.areas) {
    const sessions = data.areas[area].sessions[today] || {};
    for (let task in sessions) {
      minutesToday += sessions[task];
    }
  }
  document.getElementById('minutesToday').innerText = minutesToday;

  // Barras de progreso
  const areas = ['inteligencia', 'ejercicio', 'salud_mental'];
  areas.forEach(area => {
    const xp = data.areas[area].xp;
    const level = data.areas[area].level;
    const percent = Math.min(100, Math.round(xp / level_xp_required(level) * 100));
    document.getElementById('bar' + capitalize(area)).style.width = percent + '%';
  });

  // Gráfico de barras diario
  const labels = [];
  const values = [];
  for (let day in data.areas.ejercicio.sessions) {
    labels.push(day);
    let dayTotal = 0;
    for (let task in data.areas.ejercicio.sessions[day]) {
      dayTotal += data.areas.ejercicio.sessions[day][task];
    }
    values.push(dayTotal);
  }

  const ctx = document.getElementById('xpChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Minutos por día',
        data: values,
        backgroundColor: 'rgba(160,82,45,0.7)',
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

// Funciones auxiliares
function level_xp_required(level) {
  return Math.round(50 * Math.pow(1.01, level-1));
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

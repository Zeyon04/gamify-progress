let viewMode = 'day'; // día o mes

async function loadData() {
  const res = await fetch('../data/data.json');
  const data = await res.json();
  updateDashboard(data);
}

function updateDashboard(data) {
  // --- Minutos del día ---
  let today = new Date().toISOString().split('T')[0];
  let minutesToday = 0;
  for (let area in data.areas) {
    const sessions = data.areas[area].sessions[today] || {};
    for (let t in sessions) {
      minutesToday += sessions[t];
    }
  }
  document.getElementById('todayMinutes').innerText = minutesToday;

  // --- Barras horizontales de XP ---
  const areas = ['inteligencia','ejercicio','salud_mental'];
  const bars = ['barInt','barEj','barSalud'];
  const spans = ['xpInt','xpEj','xpSalud'];

  areas.forEach((a,i)=>{
    const xp = data.areas[a].xp || 0;
    document.getElementById(spans[i]).innerText = xp + ' XP';
    document.getElementById(bars[i]).style.width = Math.min(xp,100) + '%';
  });

  // --- Gráfico histórico ---
  const ctx = document.getElementById('xpCanvas').getContext('2d');
  if (window.xpChart) window.xpChart.destroy();

  const labels = [];
  const datasets = areas.map(a=>({label:a,data:[],backgroundColor: rgbColor(a)}));

  // Recorrer fechas
  let dates = Object.keys(data.areas[areas[0]].sessions).sort();
  dates.forEach(d=>{
    labels.push(d);
    areas.forEach((a,j)=>{
      const sum = Object.values(data.areas[a].sessions[d]||{}).reduce((x,y)=>x+y,0);
      datasets[j].data.push(sum);
    });
  });

  window.xpChart = new Chart(ctx,{
    type:'bar',
    data:{labels,datasets},
    options:{
      responsive:true,
      scales:{y:{beginAtZero:true}}
    }
  });
}

function rgbColor(area){
  if(area==='inteligencia') return 'rgba(255,0,0,0.7)';
  if(area==='ejercicio') return 'rgba(0,255,0,0.7)';
  if(area==='salud_mental') return 'rgba(0,0,255,0.7)';
}

function setView(mode){
  viewMode = mode;
  loadData();
}

// Inicializar
loadData();

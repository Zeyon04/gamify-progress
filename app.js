let sessions = JSON.parse(localStorage.getItem('sessions') || '[]');
let timer = null, startTs = 0, currentTask = null;

function start(task, area) {
  if (timer) return;
  currentTask = { area, task };
  startTs = Date.now();
  updateStatus(`Grabando: ${task} (${area})...`);
  timer = setInterval(() => {
    const mins = Math.floor((Date.now() - startTs) / 60000);
    updateStatus(`Grabando: ${task} (${mins} min)`);
  }, 1000);
}

function stop() {
  if (!timer) return;
  clearInterval(timer);
  timer = null;
  const mins = Math.max(1, Math.round((Date.now() - startTs) / 60000));
  const date = new Date().toISOString().slice(0, 10);
  sessions.push({ date, area: currentTask.area, task: currentTask.task, minutes: mins });
  localStorage.setItem('sessions', JSON.stringify(sessions));
  updateStatus(`Guardado ${mins} min de ${currentTask.task}`);
  currentTask = null;
}

function exportToday() {
  const today = new Date().toISOString().slice(0, 10);
  const todays = sessions.filter(s => s.date === today);
  const food_ok = document.getElementById("food").checked;
  const sleep_ok = document.getElementById("sleep").checked;
  const payload = { user: "oscar", date: today, sessions: todays, food_ok, sleep_ok };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `export_${today}.json`;
  a.click();
  updateStatus("Archivo exportado ✅");
}

function updateStatus(text) {
  document.getElementById("status").innerText = text;
}

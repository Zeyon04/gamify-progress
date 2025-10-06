let sessions = JSON.parse(localStorage.getItem('sessions') || '[]');

let currentTask = null;
let taskStart = 0;
let taskTimer = null;

let sleepStart = 0;
let sleepTimer = null;

// --- Funciones para tareas ---
const taskButtons = document.querySelectorAll(".task-btn");
taskButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    const task = btn.dataset.task;
    const area = btn.dataset.area;

    if (currentTask && currentTask.btn === btn) {
      stopTask();
      return;
    }

    if (currentTask) stopTask();

    currentTask = { task, area, btn };
    taskStart = Date.now();
    btn.classList.add("active");
    updateStatus(`Grabando: ${task} (${area})...`);

    taskTimer = setInterval(() => {
      const elapsed = Date.now() - taskStart;
      btn.querySelector(".timer").innerText = msToTime(elapsed);
    }, 1000);
  });
});

function stopTask() {
  if (!currentTask) return;
  clearInterval(taskTimer);

  const elapsed = Date.now() - taskStart;
  const mins = Math.max(1, Math.round(elapsed / 60000));
  const now = new Date();
  const today = now.toLocaleDateString('sv-SE'); // YYYY-MM-DD local
  const timestamp = now.toLocaleTimeString('es-ES', { hour12: false }); // HH:MM:SS local

  let existing = sessions.find(s => s.date === today && s.task === currentTask.task);
  if (!existing || mins > existing.minutes) {
    if (existing) existing.minutes = mins;
    else sessions.push({ date: today, time: timestamp, area: currentTask.area, task: currentTask.task, minutes: mins });
  }

  currentTask.btn.classList.remove("active");
  currentTask.btn.querySelector(".timer").innerText = "00:00:00";
  updateStatus(`Guardado ${mins} min de ${currentTask.task}`);
  currentTask = null;
}

// --- Cronómetro dormir ---
const sleepBtn = document.getElementById("sleepBtn");
sleepBtn.addEventListener("click", () => {
  if (sleepTimer) {
    stopSleep();
    return;
  }
  sleepStart = Date.now();
  sleepBtn.classList.add("active");
  sleepTimer = setInterval(() => {
    const elapsed = Date.now() - sleepStart;
    sleepBtn.querySelector(".timer").innerText = msToTime(elapsed);
  }, 1000);
});

function stopSleep() {
  if (!sleepTimer) return;
  clearInterval(sleepTimer);

  const elapsed = Date.now() - sleepStart;
  const mins = Math.round(elapsed / 60000);
  sleepBtn.classList.remove("active");
  sleepBtn.querySelector(".timer").innerText = "00:00:00";

  const now = new Date();
  const today = now.toLocaleDateString('sv-SE');
  const timestamp = now.toLocaleTimeString('es-ES', { hour12: false });
  let existing = sessions.find(s => s.date === today && s.task === "dormir");
  if (!existing || mins > existing.minutes) {
    if (existing) existing.minutes = mins;
    else sessions.push({ date: today, time: timestamp, area: "salud_mental", task: "dormir", minutes: mins });
  }

  updateStatus(`Dormir registrado: ${mins} min`);
  sleepTimer = null;
}

// --- Exportar ---
document.getElementById("exportBtn").addEventListener("click", exportToday);

function exportToday() {
  const now = new Date();
  const today = now.toLocaleDateString('sv-SE');

  // Hora local
  const localTime = now.toLocaleTimeString('es-ES', { hour12: false }); // "HH:MM:SS"

  const todays = [];
  sessions.forEach(s => {
    if (s.date === today) {
      let existing = todays.find(t => t.task === s.task);
      if (!existing || s.minutes > existing.minutes) {
        if (existing) Object.assign(existing, s);
        else todays.push({...s});
      }
    }
  });

  const food_ok = document.getElementById("food").checked;
  const sleep_ok = todays.some(t => t.task === "dormir" && t.minutes >= 480);
  const dinner_ok = document.getElementById("dinner").checked;

  const payload = { user: "oscar", date: today, time: localTime, sessions: todays, food_ok, dinner_ok, sleep_ok, processed: false };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `export_${today}-${localTime.replace(/:/g,"-")}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);

  // Popup amarillo
  const popup = document.createElement("div");
  popup.style.position = "fixed";
  popup.style.top = "50%";
  popup.style.left = "50%";
  popup.style.transform = "translate(-50%, -50%)";
  popup.style.background = "#FFD700";  // amarillo
  popup.style.color = "#000";          // texto negro
  popup.style.padding = "1.5rem 2rem";
  popup.style.borderRadius = "12px";
  popup.style.boxShadow = "0 5px 15px rgba(0,0,0,0.3)";
  popup.style.zIndex = "1000";
  popup.style.textAlign = "center";
  popup.style.fontSize = "1.2rem";
  popup.innerHTML = `🎉 Felicidades, progreso actualizado!\n<br><br>` +
                    todays.map(s => `${s.task}: ${s.minutes} min`).join("<br>") +
                    (food_ok ? "<br>Comida OK ✅" : "") +
                    (dinner_ok ? "<br>Cena OK ✅" : "") +
                    (sleep_ok ? "<br>Sueño OK ✅" : "");

  document.body.appendChild(popup);

  setTimeout(() => {
    popup.remove();
  }, 3500);

  updateStatus("Archivo exportado ✅");
}

// --- Helpers ---
function updateStatus(text) {
  document.getElementById("status").innerText = text;
}

function msToTime(duration) {
  let seconds = Math.floor((duration / 1000) % 60),
      minutes = Math.floor((duration / (1000 * 60)) % 60),
      hours = Math.floor(duration / (1000 * 60 * 60));
  return [hours, minutes, seconds].map(v => v.toString().padStart(2,'0')).join(':');
}

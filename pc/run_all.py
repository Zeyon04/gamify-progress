# pc/run_all.py
import os
import glob
import json
import matplotlib.pyplot as plt
from core import process_day

# Rutas
DATA_PATH = "../data/data.json"
SESSION_DIR = "session_exports"

# 1️⃣ Cargar estado acumulado
try:
    with open(DATA_PATH, "r") as f:
        state = json.load(f)
except FileNotFoundError:
    state = {
        "areas": {
            "inteligencia": {"xp": 0, "xp_rate": 1.0, "streak": 0, "days_missed": 0, "recovery_streak": 0, "penalty_applied": False},
            "ejercicio": {"xp": 0, "xp_rate": 1.0, "streak": 0, "days_missed": 0, "recovery_streak": 0, "penalty_applied": False},
            "salud_mental": {"xp": 0, "xp_rate": 1.0, "streak": 0, "days_missed": 0, "recovery_streak": 0, "penalty_applied": False}
        },
        "global_buff": 0.0
    }

# 2️⃣ Procesar todos los JSON en session_exports
json_files = glob.glob(os.path.join(SESSION_DIR, "*.json"))
if not json_files:
    print("⚠️ No se encontraron archivos JSON en session_exports.")
else:
    for jf in sorted(json_files):
        with open(jf, "r") as f:
            payload = json.load(f)
        state = process_day(state, payload)
        print(f"✅ Procesado: {os.path.basename(jf)}")

# 3️⃣ Guardar estado actualizado
with open(DATA_PATH, "w") as f:
    json.dump(state, f, indent=2)
print("✅ Estado acumulado actualizado.")

# 4️⃣ Visualizar progreso
areas = state["areas"]
names, xps, levels = [], [], []

def level_from_xp(xp):
    lvl, threshold = 1, 50
    while xp >= threshold:
        xp -= threshold
        threshold = int(threshold * 1.01)
        lvl += 1
    return lvl, xp, threshold

for area, info in areas.items():
    lvl, rem, nxt = level_from_xp(info.get("xp", 0))
    names.append(area)
    xps.append(info.get("xp", 0))
    levels.append(lvl)

plt.bar(names, xps, color="skyblue")
for i, lvl in enumerate(levels):
    plt.text(i, xps[i] + 10, f"Lvl {lvl}", ha="center", fontsize=10)
plt.title("Progreso por Área")
plt.ylabel("XP total")
plt.tight_layout()
plt.show()

import math, json, os

# =====================
# CONFIGURACIÓN GENERAL
# =====================

BASE_XP = {
    "estudiar": 1.0,
    "lectura": 0.25,
    "entrenar": 1.0,
    "andar": 0.25,
    "meditar": 1.0,
    "organizar": 1.0
}

AREA_TASKS = {
    "inteligencia": ["estudiar", "lectura"],
    "ejercicio": ["entrenar", "andar"],
    "salud_mental": ["meditar", "organizar"]
}

# Mínimos diarios por área
MIN_REQ = {
    "inteligencia": {"estudiar": 30},
    "ejercicio": {"entrenar": 30},
    "salud_mental": {"meditar": 10}
}

# Parámetros
GLOBAL_BUFF_FOOD = 0.02
GLOBAL_BUFF_SLEEP = 0.02
MAX_RATE = 3.0   # 300%
MIN_RATE = 0.0
BASE_RATE = 1.0
RATE_DROP = 0.10
XP_PENALTY = 100  # XP restado cuando el rate llega a 0%

# =====================
# FUNCIONES DE BUFFOS
# =====================

def buff_task(task, minutes):
    """Devuelve el buffo generado por una tarea concreta según sus minutos."""
    if task in ["estudiar", "entrenar", "organizar"]:
        return 0.1 * (1 - math.exp(-minutes / 80))
    elif task in ["lectura", "andar"]:
        return 0.1 * (1 - math.exp(-minutes / 800))
    elif task == "meditar":
        return 0.1 * (1 - math.exp(-minutes / 20))
    else:
        return 0

def required_met(area, tasks):
    """Comprueba si se cumplen los mínimos diarios de un área."""
    req = MIN_REQ.get(area, {})
    for t, min_req in req.items():
        if tasks.get(t, 0) < min_req:
            return False
    return True

def level_xp_required(level):
    """Devuelve la XP necesaria para pasar de un nivel al siguiente."""
    return int(round(50 * (1.01 ** (level - 1))))

# =====================
# LÓGICA PRINCIPAL
# =====================

def compute_day(state, payload):
    date = payload["date"]
    sessions = payload["sessions"]
    food_ok = payload.get("food_ok", False)
    sleep_ok = payload.get("sleep_ok", False)

    # --- Agrupar minutos por área ---
    minutes_by_area = {a: {} for a in AREA_TASKS}
    for s in sessions:
        area, task, mins = s["area"], s["task"], s["minutes"]
        minutes_by_area.setdefault(area, {})
        minutes_by_area[area][task] = minutes_by_area[area].get(task, 0) + mins

    # --- Bufo global para este día ---
    global_buff = 0.0
    if food_ok: global_buff += GLOBAL_BUFF_FOOD
    if sleep_ok: global_buff += GLOBAL_BUFF_SLEEP

    # --- Procesar cada área ---
    for area, tasks in minutes_by_area.items():
        area_state = state["areas"].setdefault(area, {
            "xp": 0,
            "level": 1,
            "rate": BASE_RATE
        })

        # Calcular buffos específicos del área
        buff_area = 0
        for t, mins in tasks.items():
            buff_area += buff_task(t, mins)

        # Aplicar buffo: sube la tasa del área
        area_state["rate"] = min(area_state["rate"] + buff_area, MAX_RATE)

        # Comprobar si se cumplieron los mínimos
        if not required_met(area, tasks):
            if area_state["rate"] > BASE_RATE:
                area_state["rate"] = BASE_RATE
            else:
                area_state["rate"] = max(MIN_RATE, area_state["rate"] - RATE_DROP)
                if area_state["rate"] == 0:
                    area_state["xp"] = max(0, area_state["xp"] - XP_PENALTY)

        # Calcular XP ganada
        xp_gained = 0
        for t, mins in tasks.items():
            base_rate = BASE_XP.get(t, 0)
            xp_gained += base_rate * mins * area_state["rate"]

        # Aplicar bufo global diario
        xp_gained *= (1 + global_buff)
        xp_gained = int(round(xp_gained))

        area_state["xp"] += xp_gained

        # Subida de nivel
        while area_state["xp"] >= level_xp_required(area_state["level"]):
            area_state["xp"] -= level_xp_required(area_state["level"])
            area_state["level"] += 1

    state["last_date"] = date
    return state

# =====================
# FUNCIONES AUXILIARES
# =====================

def load_state(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"areas": {}}

def save_state(state, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

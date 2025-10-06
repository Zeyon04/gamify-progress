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
    """
    Procesa un JSON de sesión, acumulando minutos y calculando XP y buffs
    solo al final del día (si aún no se ha procesado ese día).
    """
    date = payload["date"]
    sessions = payload.get("sessions", [])
    food_ok = payload.get("food_ok", False)
    sleep_ok = payload.get("sleep_ok", False)

    # --- Acumular minutos en el registro diario ---
    for s in sessions:
        area = s["area"]
        task = s["task"]
        mins = s["minutes"]

        area_state = state["areas"].setdefault(area, {})
        area_state.setdefault("sessions", {})
        area_state["sessions"].setdefault(date, {})
        area_state["sessions"][date][task] = area_state["sessions"][date].get(task, 0) + mins

    # --- Determinar si se debe procesar XP de este día ---
    last_date = state.get("last_processed_date")
    if last_date is not None and date <= last_date:
        # Ya se procesó XP de este día, solo acumulamos minutos
        return state

    # --- Procesar XP y buffs solo una vez por día ---
    minutes_by_area = {a: {} for a in AREA_TASKS}
    for area, area_state in state["areas"].items():
        tasks_today = area_state.get("sessions", {}).get(date, {})
        for t, mins in tasks_today.items():
            minutes_by_area[area][t] = mins

    # Buff global diario
    global_buff = 0.0
    if food_ok:
        global_buff += GLOBAL_BUFF_FOOD
    if sleep_ok:
        global_buff += GLOBAL_BUFF_SLEEP

    # --- Procesar cada área ---
    for area, tasks in minutes_by_area.items():
        area_state = state["areas"].setdefault(area, {
            "xp": 0,
            "level": 1,
            "rate": BASE_RATE
        })

        buff_area = sum(buff_task(t, mins) for t, mins in tasks.items())
        area_state["rate"] = min(area_state.get("rate", BASE_RATE) + buff_area, MAX_RATE)

        # Verificar mínimos diarios
        if not required_met(area, tasks):
            if area_state["rate"] > BASE_RATE:
                area_state["rate"] = BASE_RATE
            else:
                area_state["rate"] = max(MIN_RATE, area_state["rate"] - RATE_DROP)
                if area_state["rate"] == 0:
                    area_state["xp"] = max(0, area_state["xp"] - XP_PENALTY)

        # Calcular XP ganada
        xp_gained = sum(BASE_XP.get(t,0) * mins * area_state["rate"] for t, mins in tasks.items())
        xp_gained *= (1 + global_buff)
        xp_gained = int(round(xp_gained))
        area_state["xp"] += xp_gained

        # Subida de nivel
        while area_state["xp"] >= level_xp_required(area_state.get("level", 1)):
            area_state["xp"] -= level_xp_required(area_state.get("level", 1))
            area_state["level"] = area_state.get("level", 1) + 1

    # Actualizar fecha procesada
    state["last_processed_date"] = date
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

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
    Acumula minutos del día actual. 
    Solo procesa XP y buffs del día anterior cuando llega un nuevo día.
    """
    date = payload["date"]
    sessions = payload.get("sessions", [])
    food_ok = payload.get("food_ok", False)
    sleep_ok = payload.get("sleep_ok", False)

    # --- Acumular minutos en sessions ---
    for s in sessions:
        area = s["area"]
        task = s["task"]
        mins = s["minutes"]

        area_state = state["areas"].setdefault(area, {})
        area_state.setdefault("sessions", {})
        area_state["sessions"].setdefault(date, {})
        area_state["sessions"][date][task] = area_state["sessions"][date].get(task, 0) + mins

    # --- Revisar si hay un día anterior que procesar ---
    last_date = state.get("last_processed_date")
    if last_date is not None and date > last_date:
        # Procesar XP y buffs del día anterior
        process_day_for_date(state, last_date)

    # No se procesa XP todavía para el día actual, solo se acumulan minutos
    return state


def process_day_for_date(state, date):
    """
    Procesa XP y buffs/debuffs para un día específico.
    """
    # Buffs diarios globales
    food_ok = True if date in state.get("food_log", {}) else False
    sleep_ok = True if date in state.get("sleep_log", {}) else False
    global_buff = 0.0
    if food_ok: global_buff += GLOBAL_BUFF_FOOD
    if sleep_ok: global_buff += GLOBAL_BUFF_SLEEP

    for area, area_state in state["areas"].items():
        tasks = area_state.get("sessions", {}).get(date, {})

        # Inicializar si no existe
        area_state.setdefault("xp", 0)
        area_state.setdefault("level", 1)
        area_state.setdefault("rate", BASE_RATE)

        # Buff específico por tareas
        buff_area = sum(buff_task(t, mins) for t, mins in tasks.items())
        area_state["rate"] = min(area_state["rate"] + buff_area, MAX_RATE)

        # Comprobar mínimos diarios
        if not required_met(area, tasks):
            if area_state["rate"] > BASE_RATE:
                area_state["rate"] = BASE_RATE
            else:
                area_state["rate"] = max(MIN_RATE, area_state["rate"] - RATE_DROP)
                if area_state["rate"] == 0:
                    area_state["xp"] = max(0, area_state["xp"] - XP_PENALTY)

        # XP ganada
        xp_gained = sum(BASE_XP.get(t,0) * mins * area_state["rate"] for t, mins in tasks.items())
        xp_gained *= (1 + global_buff)
        xp_gained = int(round(xp_gained))
        area_state["xp"] += xp_gained

        # Subida de nivel
        while area_state["xp"] >= level_xp_required(area_state["level"]):
            area_state["xp"] -= level_xp_required(area_state["level"])
            area_state["level"] += 1

    # Actualizar fecha procesada
    state["last_processed_date"] = date


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

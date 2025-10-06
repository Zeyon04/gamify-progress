import json
import os
from core import compute_day

DATA_PATH = "../data/data.json"
EXPORTS_PATH = "../session_exports"  # carpeta donde metes los .json del móvil

def load_state():
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"areas": {}}

def save_state(state):
    with open(DATA_PATH, "w") as f:
        json.dump(state, f, indent=2)

def import_file(file_path):
    """Procesa un único archivo JSON exportado desde el móvil y acumula minutos del mismo día."""
    state = load_state()
    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Compatibilidad: si no existen los campos nuevos, los añadimos por defecto
    payload.setdefault("food_ok", False)
    payload.setdefault("sleep_ok", False)

    # --- Acumular minutos de sesiones del mismo día ---
    for s in payload.get("sessions", []):
        area = s["area"]
        task = s["task"]
        mins = s["minutes"]
        date = s["date"]

        area_state = state["areas"].setdefault(area, {})
        area_state.setdefault("sessions", {})
        area_state["sessions"].setdefault(date, {})
        area_state["sessions"][date][task] = area_state["sessions"][date].get(task, 0) + mins

    # --- Calcular XP y actualizar estado usando el payload completo ---
    updated = compute_day(state, payload)
    save_state(updated)
    print(f"✅ Datos actualizados desde {os.path.basename(file_path)}")


def import_all():
    """Procesa automáticamente todos los archivos en session_exports."""
    if not os.path.exists(EXPORTS_PATH):
        print("❌ No existe la carpeta session_exports.")
        return

    files = [f for f in os.listdir(EXPORTS_PATH) if f.endswith(".json")]
    if not files:
        print("ℹ️ No hay archivos JSON para importar.")
        return

    for f in sorted(files):
        file_path = os.path.join(EXPORTS_PATH, f)
        import_file(file_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        import_all()
    else:
        import_file(sys.argv[1])

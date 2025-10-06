import json
import os
from core import compute_day

DATA_PATH = "../data/data.json"
EXPORTS_PATH = "./session_exports"  # carpeta donde metes los .json del móvil

def load_state():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Inicializa con estructura vacía si no existe
        return {
            "areas": {
                "inteligencia": {"xp": 0, "level": 1, "rate": 1.0, "sessions": {}},
                "ejercicio": {"xp": 0, "level": 1, "rate": 1.0, "sessions": {}},
                "salud_mental": {"xp": 0, "level": 1, "rate": 1.0, "sessions": {}}
            },
            "last_processed_date": None,
            "food_log": {},
            "sleep_log": {}
        }

def save_state(state):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def import_file(file_path):
    """Procesa un único JSON exportado desde el móvil."""
    state = load_state()
    with open(file_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Compatibilidad campos nuevos
    payload.setdefault("food_ok", False)
    payload.setdefault("sleep_ok", False)
    payload.setdefault("processed", False)

    if not payload["processed"]:
        updated = compute_day(state, payload)
        save_state(updated)
        payload["processed"] = True  # marcar como leído
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"✅ Datos actualizados desde {os.path.basename(file_path)}")
    else:
        print(f"ℹ️ {os.path.basename(file_path)} ya procesado, se omite.")

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

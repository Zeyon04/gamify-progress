import json
from core import process_day

DATA_PATH = "../data/data.json"

def load_state():
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"areas": {}}

def save_state(state):
    with open(DATA_PATH, "w") as f:
        json.dump(state, f, indent=2)

def main(input_path):
    state = load_state()
    with open(input_path, "r") as f:
        payload = json.load(f)
    updated = process_day(state, payload)
    save_state(updated)
    print("✅ Datos actualizados:", input_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python import_sessions.py archivo.json")
    else:
        main(sys.argv[1])

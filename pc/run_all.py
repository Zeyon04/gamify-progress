import http.server
import socketserver
import threading
import webbrowser
import os
import sys
from pathlib import Path
import runpy

# ===== CONFIGURACIÓN =====
ROOT = Path(__file__).parent.resolve()          # /gamify-progress/pc
PROJECT_ROOT = ROOT.parent                      # /gamify-progress
PORT = 8000

# ===== 1. Ejecutar import_sessions.py =====
try:
    print("🔄 Procesando sesiones...")
    runpy.run_path(str(ROOT / "import_sessions.py"), run_name="__main__")
    print("✅ data.json actualizado correctamente.\n")
except Exception as e:
    print(f"⚠️ Error al ejecutar import_sessions.py: {e}\n")

# ===== 2. Iniciar servidor HTTP local =====
def start_server():
    os.chdir(PROJECT_ROOT)  # Servir todo el proyecto
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Servidor activo en http://localhost:{PORT}")
        httpd.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

# ===== 3. Abrir automáticamente el display del PC =====
display_url = f"http://localhost:{PORT}/pc/index.html"
print(f"🖥️ Abriendo display del PC: {display_url}")
webbrowser.open(display_url)

# ===== 4. Mantener el servidor hasta que cierres =====
input("\nPresiona Enter para cerrar el servidor...\n")
print("🛑 Servidor detenido.")

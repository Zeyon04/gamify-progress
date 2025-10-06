from import_sessions import import_all
import webbrowser
import os

if __name__ == "__main__":
    import_all()

index_path = os.path.join(os.path.dirname(__file__), "index.html")
webbrowser.open(f"file:///{os.path.abspath(index_path)}")
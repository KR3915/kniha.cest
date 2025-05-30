import os
import subprocess

# Global application paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(APP_DIR, "exports")

def ensure_exports_dir():
    """Zajistí, že složka pro exporty existuje."""
    if not os.path.exists(EXPORTS_DIR):
        os.makedirs(EXPORTS_DIR)

def get_exports_path():
    """Vrátí absolutní cestu ke složce s exporty."""
    ensure_exports_dir()
    return EXPORTS_DIR

def open_exports_folder():
    """Otevře složku s exporty v průzkumníku Windows."""
    ensure_exports_dir()
    subprocess.run(['explorer', EXPORTS_DIR]) 
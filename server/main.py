import customtkinter as ctk
import database
from export_utils import ensure_exports_dir
import login_screen # Předpokládáme, že login_screen.py bude existovat

APP_NAME = "Kniha.cest"

def main():
    """Hlavní funkce pro spuštění aplikace."""
    # Inicializace databáze a adresářů (mělo by se dít jen jednou)
    database.initialize_db()
    ensure_exports_dir()

    # Vytvoření hlavního okna aplikace
    app_window = ctk.CTk()
    app_window.title(f"{APP_NAME} - Přihlášení") # Počáteční titulek
    # Geometrii a další nastavení okna si řídí create_login_widgets
    
    # Zobrazení přihlašovací obrazovky
    # Funkce v login_screen.py by měla přijmout toto hlavní okno
    login_screen.create_login_widgets(app_window)

    app_window.mainloop()

if __name__ == "__main__":
    main() 
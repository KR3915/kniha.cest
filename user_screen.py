import tkinter as tk
from tkinter import ttk  # For the Combobox widget (dropdown)
import sys
import json

def load_routes(file, username):
    """Loads routes specific to the given username from the JSON file."""
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            for user_data in data.get("users", []):
                if user_data.get("username") == username:
                    return user_data.get("trasy", [])  # Return list of routes
            return []  # Return empty list if user or routes not found
    except FileNotFoundError:
        print(f"Error: {file} not found!")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file}!")
        return []

def show_route_details():
    """Displays the distance and destination of the selected route."""
    selected_route_name = route_combo.get()
    for route in user_routes:
        if route["name"] == selected_route_name:
            distance = route.get("distance", "N/A")
            destination = route.get("destination", "N/A")
            details_label.config(text=f"Cíl: {destination}, Vzdálenost: {distance}")
            return
    details_label.config(text="Vyberte trasu")

def print_number():
    print("123")

def show_page2():
    """Show page 2 and hide page 1."""
    page1.pack_forget()  # Hide page 1
    page2.pack()        # Show page 2
    root.update_idletasks()  # Force update of Combobox!

def show_page1():
    """Show page 1 and hide page 2."""
    page2.pack_forget()  # Hide page 2
    page1.pack()        # Show page 1

if __name__ == "__main__":
    username = "Neznámý uživatel"  # Default value if no username is passed
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Uživatelské jméno přihlášeného uživatele: {username}")

    # Load user-specific routes
    user_routes = load_routes("login.json", username)
    route_names = [route["name"] for route in user_routes]  # Extract route names

    # Create the main window
    root = tk.Tk()
    root.title(f"Uživatelská obrazovka pro {username}")
    root.geometry("400x400")  # Increased window size

    # Page 1 (Dashboard)
    page1 = tk.Frame(root)
    page1.pack(pady=20)

    welcome_label = tk.Label(page1, text=f"Vítejte, {username}!", font=("Arial", 16))
    welcome_label.pack(pady=10)

    nastavit_trasu_button = tk.Button(page1, text="Nastavit trasu", command=show_page2, padx=20, pady=10)
    nastavit_trasu_button.pack()

    # Page 2 (Nastavit trasu)
    page2 = tk.Frame(root)

    zpet_button = tk.Button(page2, text="Zpět na dashboard", command=show_page1, padx=20, pady=10)
    zpet_button.pack(pady=20)

    # Dropdown for selecting routes
    route_label = tk.Label(page2, text="Vyberte trasu:")
    route_label.pack(pady=5)
    route_combo = ttk.Combobox(page2, values=route_names, state="readonly")  # User can only select
    route_combo.pack(pady=5)
    route_combo.bind("<<ComboboxSelected>>", lambda event: show_route_details())  # Call function on selection

    # Label to display route details
    details_label = tk.Label(page2, text="Vyberte trasu", font=("Arial", 12))
    details_label.pack(pady=10)

    number_button = tk.Button(page2, text="Vytisknout číslo", command=print_number, padx=20, pady=10)
    number_button.pack()

    # Initially show page 1
    page1.pack()
    page2.pack_forget()

    # Run the Tkinter event loop
    root.mainloop()
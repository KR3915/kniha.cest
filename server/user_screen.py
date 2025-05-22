import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import requests
import database 
import json
import math
import random
import time # Nový import pro práci s časem

# --- Styling Constants (Minimalist Theme) ---
BG_COLOR = "#dbd8d8"
FG_COLOR = "#333333"
BUTTON_BG = "#e0e0e0"
BUTTON_FG = FG_COLOR
BUTTON_ACTIVE_BG = "#d0d0d0"
FONT = ("Segoe UI", 12)
TITLE_FONT = ("Segoe UI", 16, "bold")
PADDING = 10
BUTTON_PADDING_X = 20
BUTTON_PADDING_Y = 10

# Your TomTom API Key - REPLACE WITH YOUR ACTUAL KEY
# POUŽIJTE ZDE SVŮJ PLATNÝ TOMTOM API KLÍČ!
TOMTOM_API_KEY = "Guh742xz9ZSxx11iki85pe5bvprH9xL9"

# Global variables specific to the user screen
user_root = None
current_username = "Unknown User"
current_user_id = None
user_routes_tree = None
all_user_routes_cached = [] # To store all fetched route data for filtering/sorting

# Global variables for filter entries
filter_name_entry = None
filter_start_entry = None
filter_destination_entry = None
filter_fuel_var = None

# Global variables for sorting controls
current_sort_column = "name"
current_sort_order = "asc" # Default sort order

# Nová globální proměnná pro uložení callbacku pro návrat na login
_create_login_widgets_callback = None # Bude nastaveno v show_user_page


def show_user_page(parent_window, username, user_id, create_login_widgets_callback_func):
    """
    Zobrazí uživatelský panel.
    :param parent_window: Kořenové okno Tkinteru.
    :param username: Uživatelské jméno přihlášeného uživatele.
    :param user_id: ID přihlášeného uživatele.
    :param create_login_widgets_callback_func: Callback funkce z login_screen pro návrat zpět na login.
    """
    global user_root, current_username, current_user_id, _create_login_widgets_callback, all_user_routes_cached

    user_root = parent_window
    current_username = username
    current_user_id = user_id
    _create_login_widgets_callback = create_login_widgets_callback_func # Uložení callbacku

    user_root.title(f"Uživatelský panel pro {current_username}")
    user_root.geometry("1000x750") # Zvětšeno pro více sloupců
    user_root.deiconify() # Ensure the window is visible

    for widget in user_root.winfo_children():
        widget.destroy()

    # Reset cached data when user page is shown
    all_user_routes_cached = []
    create_user_page_layout()

def create_user_page_layout():
    """Vytvoří rozložení prvků uživatelského panelu."""
    global user_routes_tree, filter_name_entry, filter_start_entry, filter_destination_entry, filter_fuel_var, current_sort_column, current_sort_order

    # Style configuration
    style = ttk.Style(user_root)
    style.theme_use("clam")
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TEntry", font=FONT)
    style.configure("TButton", font=FONT, background=BUTTON_BG, foreground=BUTTON_FG, padding=(BUTTON_PADDING_X, BUTTON_PADDING_Y))
    style.map("TButton", background=[("active", BUTTON_ACTIVE_BG)])


    # Specific style for small sort buttons
    style.configure("Sort.TButton", font=("Segoe UI", 10), padding=(5, 2)) # Menší padding
    style.map("Sort.TButton", background=[("active", BUTTON_ACTIVE_BG)])


    style.configure("Treeview", font=FONT, rowheight=25)
    style.configure("Treeview.Heading", font=(FONT[0], FONT[1], "bold"))
    style.map("Treeview", background=[("selected", "#347083")])
    style.configure("TCheckbutton", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TRadiobutton", background=BG_COLOR, foreground=FG_COLOR, font=FONT)
    style.configure("TCombobox", font=FONT)


    main_frame = ttk.Frame(user_root, padding=PADDING)
    main_frame.pack(fill="both", expand=True)

    # Title
    title_label = ttk.Label(main_frame, text=f"Vítejte, {current_username}! Správa tras", font=TITLE_FONT)
    title_label.pack(pady=(0, PADDING * 2))

    # --- Filtering and Sorting Section ---
    filter_sort_frame = ttk.LabelFrame(main_frame, text="Filtrování a řazení tras", padding=PADDING)
    filter_sort_frame.pack(fill="x", pady=PADDING)

    # Filter entries
    filter_controls_frame = ttk.Frame(filter_sort_frame)
    filter_controls_frame.pack(fill="x", pady=5)
    filter_controls_frame.columnconfigure(1, weight=1) # Make entry columns expand

    ttk.Label(filter_controls_frame, text="Název:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    filter_name_entry = ttk.Entry(filter_controls_frame)
    filter_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    ttk.Label(filter_controls_frame, text="Start:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    filter_start_entry = ttk.Entry(filter_controls_frame)
    filter_start_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

    ttk.Label(filter_controls_frame, text="Cíl:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    filter_destination_entry = ttk.Entry(filter_controls_frame)
    filter_destination_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

    filter_fuel_var = tk.StringVar(value="Vše") # 'Vše', 'Ano', 'Ne'
    ttk.Radiobutton(filter_controls_frame, text="Potřeba tankovat: Vše", variable=filter_fuel_var, value="Vše").grid(row=0, column=2, padx=10, sticky="w")
    ttk.Radiobutton(filter_controls_frame, text="Potřeba tankovat: Ano", variable=filter_fuel_var, value="Ano").grid(row=1, column=2, padx=10, sticky="w")
    ttk.Radiobutton(filter_controls_frame, text="Potřeba tankovat: Ne", variable=filter_fuel_var, value="Ne").grid(row=2, column=2, padx=10, sticky="w")


    filter_button = ttk.Button(filter_sort_frame, text="Filtrovat", command=apply_filters_and_sort)
    filter_button.pack(pady=5)

    # --- Sorting Buttons ---
    sort_buttons_frame = ttk.Frame(filter_sort_frame)
    sort_buttons_frame.pack(fill="x", pady=5)

    # Define only the columns to be sortable
    sortable_columns = {
        "name": "Název",
        "distance": "Vzdálenost",
        "travel_time": "Čas cesty",
        "fuel_consumption": "Spotřeba",
        "gas_stations": "Stanice", # Pro tento sloupec se bude řadit podle počtu
        "needs_fuel": "Potřeba paliva"
    }

    # Create buttons for each sortable column (Ascending and Descending)
    sort_row_index = 0
    col_index = 0
    for col_name, display_name in sortable_columns.items():
        col_button_frame = ttk.Frame(sort_buttons_frame)
        col_button_frame.grid(row=sort_row_index, column=col_index, padx=5, pady=2, sticky="w")

        ttk.Label(col_button_frame, text=f"Seřadit podle {display_name}:").pack(side="left", padx=(0, 5))

        ttk.Button(col_button_frame, text="↑", style="Sort.TButton",
                   command=lambda c=col_name: set_sort_and_apply(c, "asc")).pack(side="left", padx=1)
        ttk.Button(col_button_frame, text="↓", style="Sort.TButton",
                   command=lambda c=col_name: set_sort_and_apply(c, "desc")).pack(side="left", padx=1)

        col_index += 1
        if col_index >= 3: # Max 3 columns per row for better layout
            col_index = 0
            sort_row_index += 1

    for i in range(3): # Assuming max 3 columns of sort buttons
        sort_buttons_frame.columnconfigure(i, weight=1)

    filter_name_entry.bind("<KeyRelease>", lambda e: apply_filters_and_sort())
    filter_start_entry.bind("<KeyRelease>", lambda e: apply_filters_and_sort())
    filter_destination_entry.bind("<KeyRelease>", lambda e: apply_filters_and_sort())
    filter_fuel_var.trace_add("write", lambda *args: apply_filters_and_sort())


    # --- Treeview for Routes ---
    routes_frame = ttk.Frame(main_frame)
    routes_frame.pack(fill="both", expand=True, pady=PADDING)

    # Updated columns to include new fields
    columns = ("name", "start_location", "destination", "distance", "travel_time", "fuel_consumption", "gas_stations", "needs_fuel")
    user_routes_tree = ttk.Treeview(routes_frame, columns=columns, show="headings")
    user_routes_tree.pack(side="left", fill="both", expand=True)

    # Define headings
    user_routes_tree.heading("name", text="Název")
    user_routes_tree.heading("start_location", text="Počáteční místo")
    user_routes_tree.heading("destination", text="Cíl")
    user_routes_tree.heading("distance", text="Vzdálenost (km)")
    user_routes_tree.heading("travel_time", text="Čas cesty (s)")
    user_routes_tree.heading("fuel_consumption", text="Spotřeba paliva (L)")
    user_routes_tree.heading("gas_stations", text="Čer. stanice (počet)")
    user_routes_tree.heading("needs_fuel", text="Potřeba paliva")


    # Column widths
    user_routes_tree.column("name", width=120, stretch=tk.YES)
    user_routes_tree.column("start_location", width=150, stretch=tk.YES)
    user_routes_tree.column("destination", width=150, stretch=tk.YES)
    user_routes_tree.column("distance", width=80, stretch=tk.YES)
    user_routes_tree.column("travel_time", width=80, stretch=tk.YES)
    user_routes_tree.column("fuel_consumption", width=100, stretch=tk.YES)
    user_routes_tree.column("gas_stations", width=100, stretch=tk.YES)
    user_routes_tree.column("needs_fuel", width=80, stretch=tk.YES)

    # Scrollbar
    scrollbar = ttk.Scrollbar(routes_frame, orient="vertical", command=user_routes_tree.yview)
    user_routes_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Bind double-click event to show gas stations dialog
    user_routes_tree.bind("<Double-1>", show_gas_stations_dialog)

    # --- Buttons for Route Management ---
    button_frame = ttk.Frame(main_frame, padding=(0, PADDING))
    button_frame.pack(fill="x", pady=PADDING)

    # Nový vnořený rámeček pro hlavní akční tlačítka (Přidat, Upravit, Smazat)
    action_buttons_frame = ttk.Frame(button_frame)
    action_buttons_frame.pack(side="left", expand=True, fill="x") # Expand tento rámeček

    ttk.Button(action_buttons_frame, text="Přidat trasu", command=add_route_dialog).pack(side="left", padx=5, expand=True)
    ttk.Button(action_buttons_frame, text="Upravit trasu", command=edit_route_dialog).pack(side="left", padx=5, expand=True)
    ttk.Button(action_buttons_frame, text="Smazat trasu", command=delete_route_confirm).pack(side="left", padx=5, expand=True)

    # Tlačítko pro vyhledání trasy podle pumpy (UPRAVENÉ)
    ttk.Button(button_frame, text="Najdi trasu poblíž pumpy", command=find_route_by_gas_station_dialog).pack(side="left", padx=5, expand=True)

    # Ostatní tlačítka
    ttk.Button(button_frame, text="Aktualizovat seznam", command=lambda: apply_filters_and_sort(force_fetch=True)).pack(side="left", padx=5, expand=True)
    ttk.Button(button_frame, text="Zpět na přihlášení", command=go_back_to_login).pack(side="right", padx=5) # pack "Zpět" na pravou stranu


    apply_filters_and_sort(force_fetch=True) # Initial load

def _make_tomtom_request(url, max_retries=5, initial_delay=1):
    """
    Pomocná funkce pro provádění HTTP GET požadavků na TomTom API
    s retry logikou pro chybu 429 Too Many Requests (exponenciální backoff).
    """
    delay = initial_delay
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=10) # Přidáno timeout pro zabránění zablokování
            response.raise_for_status() # Vyvolá HTTPError pro 4xx/5xx chyby
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"DEBUG: Obdržena chyba 429 (Too Many Requests). Pokus {i+1}/{max_retries}. Čekám {delay} sekund.")
                time.sleep(delay)
                delay *= 2 # Exponenciální nárůst zpoždění
            else:
                raise # Vyvolat jinou HTTP chybu okamžitě
        except requests.exceptions.ConnectionError as e:
            print(f"DEBUG: Chyba připojení při volání TomTom API: {e}. Pokus {i+1}/{max_retries}. Čekám {delay} sekund.")
            time.sleep(delay)
            delay *= 2
        except requests.exceptions.Timeout as e:
            print(f"DEBUG: Vypršel časový limit při volání TomTom API: {e}. Pokus {i+1}/{max_retries}. Čekám {delay} sekund.")
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            # Jiné neočekávané chyby
            print(f"DEBUG: Neočekávaná chyba při volání TomTom API: {e}")
            raise # Re-raise other exceptions

    # Pokud se dostaneme sem, všechny pokusy selhaly
    raise requests.exceptions.RequestException(f"TomTom API požadavek selhal po {max_retries} pokusech.")


def get_coords_from_location(location_name):
    """
    Získá souřadnice (lat, lon) a freeformAddress pro zadaný název místa pomocí TomTom Geocoding API.
    Vrátí (lat, lon, freeformAddress) nebo (None, None, None) při chybě.
    Používá _make_tomtom_request s retry logikou.
    """
    if not TOMTOM_API_KEY:
        messagebox.showwarning("API Klíč chybí", "TomTom API klíč není nastaven.", parent=user_root)
        return None, None, None
    try:
        geocode_url = f"https://api.tomtom.com/search/2/geocode/{requests.utils.quote(location_name)}.json?key={TOMTOM_API_KEY}&countrySet=CZ&limit=1&language=cs-CZ&typeahead=true"
        print(f"DEBUG: Geocoding URL: {geocode_url}")

        data = _make_tomtom_request(geocode_url)

        if data and data.get('results'):
            position = data['results'][0]['position']
            address = data['results'][0]['address']['freeformAddress']
            print(f"DEBUG: Nalezené souřadnice pro '{location_name}': {position['lat']}, {position['lon']} (Adresa: {address})")
            return position['lat'], position['lon'], address # Return the found address
        else:
            print(f"DEBUG: Nelze najít souřadnice pro: {location_name} v České republice. Data: {data}")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Chyba při geocodingu (po opakování): {e}")
        messagebox.showerror("Chyba API", f"Nepodařilo se získat souřadnice pro '{location_name}'. Zkontrolujte připojení nebo zadané místo. {e}", parent=user_root)
        return None, None, None
    except Exception as e:
        print(f"DEBUG: Neočekávaná chyba při geocodingu: {e}")
        messagebox.showerror("Chyba API", f"Neočekávaná chyba při geocodingu: {e}", parent=user_root)
        return None, None, None

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Vypočítá vzdálenost mezi dvěma body na Zemi pomocí Haversinovy formule.
    Vrací vzdálenost v kilometrech.
    """
    R = 6371  # Poloměr Země v kilometrech

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def fetch_route_distance(start, destination, waypoint_coords=None):
    """
    Fetches the distance, travel time, and searches for gas stations from TomTom API.
    Can include a waypoint.
    Returns (distance_km, travel_time_seconds, fuel_consumption_liters, gas_stations_list, needs_fuel, route_waypoints)
    or (None, None, None, None, False, None) on error.
    Používá _make_tomtom_request s retry logikou.
    """
    if not TOMTOM_API_KEY:
        messagebox.showwarning("API Klíč chybí", "TomTom API klíč není nastaven. Vzdálenost a služby nebudou vypočítány.", parent=user_root)
        return None, None, None, None, False, None

    start_coords_lat, start_coords_lon, _ = get_coords_from_location(start)
    if start_coords_lat is None: return None, None, None, None, False, None

    destination_coords_lat, destination_coords_lon, _ = get_coords_from_location(destination)
    if destination_coords_lat is None: return None, None, None, None, False, None

    routing_url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/"
        f"{start_coords_lat},{start_coords_lon}:"
    )

    if waypoint_coords:
        routing_url += f"{waypoint_coords[0]},{waypoint_coords[1]}:"
        routing_url += f"{destination_coords_lat},{destination_coords_lon}/json"
    else:
        routing_url += f"{destination_coords_lat},{destination_coords_lon}/json"

    routing_url += f"?key={TOMTOM_API_KEY}"
    routing_url += "&travelMode=car&traffic=true&avoid=unpavedRoads"
    routing_url += "&instructionsType=full&routeType=fastest" # Request full instructions for waypoints
    print(f"DEBUG: Routing URL: {routing_url}") # Pro debug

    try:
        # Routing
        route_data = _make_tomtom_request(routing_url)

        distance_km = 0.0
        travel_time_seconds = 0
        route_waypoints = [] # Zde uložíme waypoints trasy

        if route_data and route_data.get('routes'):
            route_summary = route_data['routes'][0]['summary']
            distance_km = route_summary['lengthInMeters'] / 1000
            travel_time_seconds = route_summary['travelTimeInSeconds']
            print(f"DEBUG: Trasa nalezena. Vzdálenost: {distance_km:.2f} km, Čas: {travel_time_seconds} s.")

            # Extract actual route points/waypoints
            # TomTom returns a list of points in legs/sections
            for leg in route_data['routes'][0]['legs']:
                for point in leg['points']:
                    route_waypoints.append((point['latitude'], point['longitude']))
            print(f"DEBUG: Získáno {len(route_waypoints)} bodů trasy.")

        else:
            print(f"DEBUG: Nelze vypočítat trasu. Data: {route_data}")
            messagebox.showwarning("Chyba trasy", "Nelze vypočítat trasu mezi zadanými místy.", parent=user_root)
            return None, None, None, None, False, None # Pokud trasa není platná, nemá smysl pokračovat


        # --- Výpočet spotřeby paliva (PLACEHOLDER) ---
        # Tato hodnota je zástupná. Reálná spotřeba závisí na typu vozidla, rychlosti atd.
        # Předpokládejme průměrnou spotřebu 7 L/100 km.
        fuel_consumption_per_100km = 7.0
        estimated_fuel_needed = (distance_km / 100) * fuel_consumption_per_100km if distance_km > 0 else 0.0

        # --- Zjištění potřeby paliva (HEURISTIKA) ---
        # Pokud je trasa delší než 100 km, předpokládáme, že bude potřeba tankovat
        needs_fuel = distance_km > 100

        # --- Vyhledání čerpacích stanic (TomTom Search API - POI Search) ---
        # Prohledáváme v okolí cíle (jednoduchá implementace)
        # Sofistikovanější by bylo prohledávat podél trasy.
        gas_stations_list = []
        # Použijeme koordináty cíle pro hledání POI.
        # Radius 10 km, limit 10 výsledků, pouze v CZ.
        poi_search_url = (
            f"https://api.tomtom.com/search/2/poiSearch/fuel%20station.json?"
            f"key={TOMTOM_API_KEY}&lat={destination_coords_lat}&lon={destination_coords_lon}&radius=10000"
            f"&limit=10&countrySet=CZ"
        )
        print(f"DEBUG: POI Search URL (Destination): {poi_search_url}")
        poi_data = _make_tomtom_request(poi_search_url)

        if poi_data and poi_data.get('results'):
            for result in poi_data['results']:
                gas_stations_list.append({
                    'name': result.get('poi', {}).get('name', 'Neznámá stanice'),
                    'address': result.get('address', {}).get('freeformAddress', 'Neznámá adresa'),
                    'lat': result.get('position', {}).get('lat'),
                    'lon': result.get('position', {}).get('lon')
                })
            print(f"DEBUG: Nalezeno {len(gas_stations_list)} čerpacích stanic v okolí cíle.")
        else:
            print(f"DEBUG: Žádné čerpací stanice v okolí cíle nenalezeny.")

        return f"{distance_km:.2f} km", travel_time_seconds, estimated_fuel_needed, gas_stations_list, needs_fuel, route_waypoints

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Chyba při získávání dat z TomTom API (routing/poi po opakování): {e}")
        messagebox.showerror("Chyba API", f"Nepodařilo se získat data trasy. Zkontrolujte připojení nebo TomTom API klíč. {e}", parent=user_root)
        return None, None, None, None, False, None
    except Exception as e:
        print(f"DEBUG: Neočekávaná chyba při získávání dat z TomTom API (routing/poi): {e}")
        messagebox.showerror("Chyba API", f"Neočekávaná chyba při získávání dat z TomTom API: {e}", parent=user_root)
        return None, None, None, None, False, None

def add_route_dialog():
    """Zobrazí dialog pro přidání nové trasy."""
    dialog = tk.Toplevel(user_root)
    dialog.title("Přidat novou trasu")
    dialog.transient(user_root) # Dialog bude nad hlavním oknem
    dialog.grab_set() # Zablokuje interakci s hlavním oknem

    dialog.geometry("400x300")
    dialog.resizable(False, False)
    dialog.configure(bg=BG_COLOR)

    dialog_frame = ttk.Frame(dialog, padding=PADDING)
    dialog_frame.pack(fill="both", expand=True)

    labels = ["Název trasy:", "Počáteční místo:", "Cíl:"]
    entries = {}
    for i, text in enumerate(labels):
        ttk.Label(dialog_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(dialog_frame)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entries[text.replace(":", "").replace(" ", "_").lower()] = entry # Store by simplified key

    # Configure column to expand
    dialog_frame.grid_columnconfigure(1, weight=1)

    def save_route():
        name = entries["název_trasy"].get().strip()
        start = entries["počáteční_místo"].get().strip()
        destination = entries["cíl"].get().strip()

        if not name or not destination:
            messagebox.showwarning("Upozornění", "Název trasy a cíl jsou povinné.", parent=dialog)
            return

        # Updated unpacking of return values - now includes route_waypoints
        distance_str, travel_time, fuel_consumption, gas_stations, needs_fuel, route_waypoints = fetch_route_distance(start, destination)

        if distance_str is None:
            # Error already handled by fetch_route_distance
            return

        # Pass all required arguments to add_route, including route_waypoints
        if database.add_route(current_user_id, name, start, destination, distance_str, travel_time, fuel_consumption, gas_stations, needs_fuel, route_waypoints):
            messagebox.showinfo("Úspěch", "Trasa úspěšně přidána.", parent=dialog)
            dialog.destroy()
            apply_filters_and_sort(force_fetch=True) # Refresh list
            # --- ZDE PŘIDÁNO: VYPSÁNÍ VŠECH TRAS DO TERMINÁLU ---
            print("\n--- Seznam všech tras po přidání/úpravě ---")
            all_routes = database.get_routes_by_user(current_user_id)
            for route in all_routes:
                print(f"ID: {route['id']}, Název: {route['name']}, Start: {route['start_location']}, Cíl: {route['destination']}, "
                      f"Vzdálenost: {route['distance']}, Čas: {route['travel_time']} s, Spotřeba: {route['fuel_consumption']:.2f} L, "
                      f"Potřeba tankovat: {'Ano' if route['needs_fuel'] else 'Ne'}, "
                      f"Čerpací stanice: {len(route['gas_stations'])} nalezeno - {route['gas_stations']}, "
                      f"Waypointy: {route.get('waypoints', 'N/A')}") # Display waypoints
            print("-------------------------------------------\n")
            # --- KONEC PŘIDANÉHO VÝPISU ---
        else:
            messagebox.showerror("Chyba", "Nepodařilo se přidat trasu. Možná název trasy již existuje.", parent=dialog)

    ttk.Button(dialog_frame, text="Uložit", command=save_route).grid(row=len(labels), column=0, columnspan=2, pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy) # Handle close button
    dialog.wait_window() # Wait until dialog is closed

def edit_route_dialog():
    """Zobrazí dialog pro úpravu vybrané trasy."""
    selected_item = user_routes_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte prosím trasu k úpravě.", parent=user_root)
        return

    # Get data of the selected item by its ID from the cached data
    # We need the full data dictionary for all columns
    selected_route_index = user_routes_tree.index(selected_item)
    selected_route_data = None
    if 0 <= selected_route_index < len(all_user_routes_cached):
        selected_route_data = all_user_routes_cached[selected_route_index]


    if not selected_route_data:
        messagebox.showerror("Chyba", "Nepodařilo se najít data pro vybranou trasu.", parent=user_root)
        return

    route_id = selected_route_data['id']
    current_name = selected_route_data['name']
    current_start = selected_route_data['start_location']
    current_destination = selected_route_data['destination']
    current_distance_str = selected_route_data['distance'] # Stále string "XXX.YY km"
    current_travel_time = selected_route_data.get('travel_time', 0)
    current_fuel_consumption = selected_route_data.get('fuel_consumption', 0.0)
    current_gas_stations = selected_route_data.get('gas_stations', []) # Bude to seznam
    current_needs_fuel = selected_route_data.get('needs_fuel', False)
    current_waypoints = selected_route_data.get('waypoints', []) # Get current waypoints


    dialog = tk.Toplevel(user_root)
    dialog.title("Upravit trasu")
    dialog.transient(user_root)
    dialog.grab_set()
    dialog.geometry("400x350")
    dialog.resizable(False, False)
    dialog.configure(bg=BG_COLOR)

    dialog_frame = ttk.Frame(dialog, padding=PADDING)
    dialog_frame.pack(fill="both", expand=True)

    labels = ["Název trasy:", "Počáteční místo:", "Cíl:"]
    entries = {}
    for i, text in enumerate(labels):
        ttk.Label(dialog_frame, text=text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(dialog_frame)
        entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entries[text.replace(":", "").replace(" ", "_").lower()] = entry

    entries["název_trasy"].insert(0, current_name)
    entries["počáteční_místo"].insert(0, current_start)
    entries["cíl"].insert(0, current_destination)

    # Checkbutton for needs_fuel
    needs_fuel_var = tk.BooleanVar(value=current_needs_fuel)
    ttk.Checkbutton(dialog_frame, text="Potřeba paliva", variable=needs_fuel_var).grid(row=len(labels), column=0, columnspan=2, padx=5, pady=5, sticky="w")

    dialog_frame.grid_columnconfigure(1, weight=1)

    def save_changes():
        new_name = entries["název_trasy"].get().strip()
        new_start = entries["počáteční_místo"].get().strip()
        new_destination = entries["cíl"].get().strip()
        final_needs_fuel = needs_fuel_var.get() # User's manual override or current value

        # Initialize with current values
        new_distance_str = current_distance_str
        new_travel_time = current_travel_time
        new_fuel_consumption = current_fuel_consumption
        new_gas_stations = current_gas_stations # Keep existing list for now
        new_waypoints = current_waypoints # Keep existing waypoints

        if not new_name or not new_destination:
            messagebox.showwarning("Upozornění", "Název trasy a cíl jsou povinné.", parent=dialog)
            return

        # Check if start or destination changed, if so, recalculate all API-dependent values
        if new_start != current_start or new_destination != current_destination:
            # Re-fetch data from TomTom API
            distance_api_str, travel_time_api, fuel_consumption_api, gas_stations_api, needs_fuel_api, waypoints_api = fetch_route_distance(new_start, new_destination)

            if distance_api_str is None:
                return # Error already shown by fetch_route_distance

            new_distance_str = distance_api_str
            new_travel_time = travel_time_api
            new_fuel_consumption = fuel_consumption_api
            new_gas_stations = gas_stations_api # Use the newly fetched list of gas stations
            new_waypoints = waypoints_api # Use newly fetched waypoints
            # final_needs_fuel is already set by needs_fuel_var.get()

        # Pass all required arguments to update_route
        if database.update_route(route_id, new_name, new_start, new_destination, new_distance_str, new_travel_time, new_fuel_consumption, new_gas_stations, final_needs_fuel, new_waypoints):
            messagebox.showinfo("Úspěch", "Trasa úspěšně aktualizována.", parent=dialog)
            dialog.destroy()
            apply_filters_and_sort(force_fetch=True) # Refresh list
            # --- ZDE PŘIDÁNO: VYPSÁNÍ VŠECH TRAS DO TERMINÁLU ---
            print("\n--- Seznam všech tras po přidání/úpravě ---")
            all_routes = database.get_routes_by_user(current_user_id)
            for route in all_routes:
                print(f"ID: {route['id']}, Název: {route['name']}, Start: {route['start_location']}, Cíl: {route['destination']}, "
                      f"Vzdálenost: {route['distance']}, Čas: {route['travel_time']} s, Spotřeba: {route['fuel_consumption']:.2f} L, "
                      f"Potřeba tankovat: {'Ano' if route['needs_fuel'] else 'Ne'}, "
                      f"Čerpací stanice: {len(route['gas_stations'])} nalezeno - {route['gas_stations']}, "
                      f"Waypointy: {route.get('waypoints', 'N/A')}") # Display waypoints
            print("-------------------------------------------\n")
            # --- KONEC PŘIDANÉHO VÝPISU ---
        else:
            messagebox.showerror("Chyba", "Nepodařilo se aktualizovat trasu. Možná název trasy již existuje.", parent=dialog)

    ttk.Button(dialog_frame, text="Uložit změny", command=save_changes).grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.wait_window()


def delete_route_confirm():
    """Potvrdí a smaže vybranou trasu."""
    selected_item = user_routes_tree.selection()
    if not selected_item:
        messagebox.showwarning("Upozornění", "Vyberte prosím trasu ke smazání.", parent=user_root)
        return

    # Get data of the selected item by its ID from the cached data
    selected_route_index = user_routes_tree.index(selected_item)
    selected_route_data = None
    if 0 <= selected_route_index < len(all_user_routes_cached):
        selected_route_data = all_user_routes_cached[selected_route_index]

    if not selected_route_data:
        messagebox.showerror("Chyba", "Nepodařilo se najít data pro vybranou trasu.", parent=user_root)
        return

    route_id = selected_route_data['id']
    selected_route_name = selected_route_data['name'] # Get name directly from data

    response = messagebox.askyesno("Potvrdit smazání", f"Opravdu chcete smazat trasu '{selected_route_name}'?", parent=user_root)
    if response:
        if database.delete_route(route_id):
            messagebox.showinfo("Úspěch", "Trasa byla úspěšně smazána.", parent=user_root)
            apply_filters_and_sort(force_fetch=True) # Refresh list
            # --- ZDE PŘIDÁNO: VYPSÁNÍ VŠECH TRAS DO TERMINÁLU ---
            print("\n--- Seznam všech tras po přidání/úpravě ---")
            all_routes = database.get_routes_by_user(current_user_id)
            for route in all_routes:
                print(f"ID: {route['id']}, Název: {route['name']}, Start: {route['start_location']}, Cíl: {route['destination']}, "
                      f"Vzdálenost: {route['distance']}, Čas: {route['travel_time']} s, Spotřeba: {route['fuel_consumption']:.2f} L, "
                      f"Potřeba tankovat: {'Ano' if route['needs_fuel'] else 'Ne'}, "
                      f"Čerpací stanice: {len(route['gas_stations'])} nalezeno - {route['gas_stations']}, "
                      f"Waypointy: {route.get('waypoints', 'N/A')}") # Display waypoints
            print("-------------------------------------------\n")
            # --- KONEC PŘIDANÉHO VÝPISU ---
        else:
            messagebox.showerror("Chyba", "Nepodařilo se smazat trasu.", parent=user_root)


def show_gas_stations_dialog(event):
    """
    Zobrazí dialog s detailem čerpacích stanic pro vybranou trasu.
    """
    selected_item = user_routes_tree.selection()
    if not selected_item:
        return # Nic vybráno

    # Zjistíme, na jaký sloupec bylo kliknuto
    column_id = user_routes_tree.identify_column(event.x)
    # Treeview columns are 1-indexed for column_id, so adjust to 0-indexed for comparison
    # However, 'id' option directly returns the column identifier string, which is what we need.
    if user_routes_tree.column(column_id, option="id") == "gas_stations":
        selected_route_index = user_routes_tree.index(selected_item[0])
        selected_route_data = None
        if 0 <= selected_route_index < len(all_user_routes_cached):
            selected_route_data = all_user_routes_cached[selected_route_index]

        if selected_route_data:
            gas_stations = selected_route_data.get('gas_stations', [])
            route_name = selected_route_data.get('name', 'Neznámá trasa')

            if not gas_stations:
                messagebox.showinfo("Čerpací stanice", f"Pro trasu '{route_name}' nebyly nalezeny žádné čerpací stanice v blízkosti cíle.", parent=user_root)
                return

            dialog = tk.Toplevel(user_root)
            dialog.title(f"Čerpací stanice pro: {route_name}")
            dialog.transient(user_root)
            dialog.grab_set()
            dialog.geometry("500x400")
            dialog.configure(bg=BG_COLOR)

            dialog_frame = ttk.Frame(dialog, padding=PADDING)
            dialog_frame.pack(fill="both", expand=True)

            ttk.Label(dialog_frame, text=f"Nalezené čerpací stanice pro '{route_name}':", font=TITLE_FONT).pack(pady=10)

            # Treeview pro seznam stanic
            station_tree = ttk.Treeview(dialog_frame, columns=("name", "address"), show="headings")
            station_tree.heading("name", text="Název stanice")
            station_tree.heading("address", text="Adresa")
            station_tree.column("name", width=150, stretch=tk.YES)
            station_tree.column("address", width=250, stretch=tk.YES)
            station_tree.pack(fill="both", expand=True, pady=5)

            # Scrollbar pro seznam stanic
            station_scrollbar = ttk.Scrollbar(station_tree, orient="vertical", command=station_tree.yview)
            station_tree.configure(yscrollcommand=station_scrollbar.set)
            station_scrollbar.pack(side="right", fill="y")


            for station in gas_stations:
                station_tree.insert("", "end", values=(station.get('name', 'Neznámý'), station.get('address', 'Neznámá')))

            ttk.Button(dialog_frame, text="Zavřít", command=dialog.destroy).pack(pady=10)
            dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
            dialog.wait_window()


def find_gas_station_coords_by_name_and_city(query_address):
    """
    Pokusí se najít souřadnice čerpací stanice na zadané adrese (nebo v jejím blízkém okolí).
    Nejprve geokóduje adresu. Poté v blízkém okolí (větší poloměr) hledá POI typu čerpací stanice.
    Vrátí (lat, lon, found_station_name, found_station_address, is_fuel_station_poi_found).
    is_fuel_station_poi_found je True, pokud byl nalezen POI typu čerpací stanice
    v dostatečné blízkosti geokódovaných souřadnic, jinak False.
    Používá _make_tomtom_request s retry logikou.
    """
    if not TOMTOM_API_KEY:
        messagebox.showwarning("API Klíč chybí", "TomTom API klíč není nastaven.", parent=user_root)
        return None, None, None, None, False

    # Krok 1: Geokódování zadané (i neúplné) adresy
    address_lat, address_lon, geocoded_freeform_address = get_coords_from_location(query_address)
    if address_lat is None or address_lon is None:
        print(f"DEBUG: Nepodařilo se geokódovat adresu: {query_address}")
        # get_coords_from_location už ukáže chybovou zprávu
        return None, None, None, None, False

    # Krok 2: Hledání POI typu "fuel station" v okolí geokódovaných souřadnic
    search_radius_meters = 1000 # 1 km radius pro hledání pump v okolí geokódované adresy
    poi_search_url = (
        f"https://api.tomtom.com/search/2/poiSearch/fuel%20station.json?"
        f"key={TOMTOM_API_KEY}&lat={address_lat}&lon={address_lon}&radius={search_radius_meters}"
        f"&limit=1&countrySet=CZ&language=cs-CZ" # Limit na 1 nejbližší
    )
    print(f"DEBUG: Hledám čerpací stanici v okolí souřadnic ({address_lat},{address_lon}) s radiusem {search_radius_meters}m: {poi_search_url}")

    try:
        poi_data = _make_tomtom_request(poi_search_url)

        if poi_data and poi_data.get('results'):
            result = poi_data['results'][0]
            # Zkontrolujeme, zda nalezený POI je skutečně "fuel station"
            is_fuel_station_category_or_code = False
            categories = result.get('poi', {}).get('categories', [])
            classifications = result.get('poi', {}).get('classifications', [])

            # Check if "fuel station" is in categories (case-insensitive)
            if "fuel station" in [c.lower() for c in categories]:
                is_fuel_station_category_or_code = True
            else:
                # Check classifications by code or name
                for classification in classifications:
                    if classification.get('code') == '7315' or \
                       'petrol station' in classification.get('names', [{'name':''}])[-1].get('name', '').lower() or \
                       'fuel station' in classification.get('names', [{'name':''}])[-1].get('name', '').lower():
                        is_fuel_station_category_or_code = True
                        break

            if is_fuel_station_category_or_code:
                found_name = result.get('poi', {}).get('name', 'Neznámá čerpací stanice')
                found_address = result.get('address', {}).get('freeformAddress', 'Neznámá adresa')
                found_lat = result['position']['lat']
                found_lon = result['position']['lon']

                dist_from_query_address_coords_to_pump = haversine_distance(address_lat, address_lon, found_lat, found_lon) * 1000 # na metry

                if dist_from_query_address_coords_to_pump <= search_radius_meters:
                    print(f"DEBUG: Nalezena čerpací stanice: '{found_name}' na adrese '{found_address}' (Souřadnice: {found_lat},{found_lon}). Vzdálenost od původně geokódované adresy: {dist_from_query_address_coords_to_pump:.2f}m")
                    return found_lat, found_lon, found_name, found_address, True
                else:
                    print(f"DEBUG: Nalezená čerpací stanice je příliš daleko od původně geokódované adresy ({dist_from_query_address_coords_to_pump:.2f}m), ignorováno.")
                    return None, None, None, None, False
            else:
                print(f"DEBUG: V okolí adresy '{query_address}' byl nalezen bod zájmu '{result.get('poi', {}).get('name', 'N/A')}', ale není to čerpací stanice.")
                return None, None, None, None, False
        else:
            print(f"DEBUG: V okolí geokódované adresy pro '{query_address}' nebyla nalezena žádná čerpací stanice. Data: {poi_data}")
            return None, None, None, None, False

    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Chyba při hledání pumpy (po opakování): {e}")
        messagebox.showerror("Chyba API", f"Nepodařilo se najít čerpací stanici. Zkontrolujte připojení nebo TomTom API klíč. {e}", parent=user_root)
        return None, None, None, None, False
    except Exception as e:
        print(f"DEBUG: Neočekávaná chyba při hledání pumpy: {e}")
        messagebox.showerror("Chyba API", f"Neočekávaná chyba při hledání pumpy: {e}", parent=user_root)
        return None, None, None, None, False


def find_route_by_gas_station_dialog():
    """
    Požádá uživatele o adresu pumpy a vypíše názvy tras z databáze, které projíždí blízko.
    Pokud žádná trasa neprojede blízko, vypíše odpovídající zprávu.
    """
    pump_input = simpledialog.askstring(
        "Zadejte adresu čerpací stanice",
        "Zadejte adresu čerpací stanice (např. 'Modřice, Brněnská 671' nebo 'Brno, Masná'):",
        parent=user_root
    )

    if pump_input is None or not pump_input.strip(): # User cancelled or entered empty string
        return

    pump_input = pump_input.strip()
    pump_lat, pump_lon, found_station_name, found_station_address, is_fuel_station_poi_found = find_gas_station_coords_by_name_and_city(pump_input)

    if not is_fuel_station_poi_found or pump_lat is None or pump_lon is None:
        messagebox.showwarning(
            "Pumpa nenalezena",
            f"Na adrese nebo v blízkosti '{pump_input}' nebyla nalezena žádná čerpací stanice. "
            "Zkuste zadat jinou, přesnější nebo úplnější adresu.",
            parent=user_root
        )
        return

    # Pokud je pumpa nalezena, získejte všechny trasy uživatele
    all_routes = database.get_routes_by_user(current_user_id)
    if not all_routes:
        messagebox.showinfo("Žádné trasy", "Ve vaší databázi nejsou uloženy žádné trasy.", parent=user_root)
        return

    found_matching_routes = []
    threshold_km = 5 # Rozsah v kilometrech, do kterého se považuje, že trasa "projíždí blízko"

    for route in all_routes:
        route_waypoints = route.get('waypoints', [])

        # Kontrola, zda start nebo cíl trasy je blízko pumpy
        start_coords_lat, start_coords_lon, _ = get_coords_from_location(route['start_location'])
        dest_coords_lat, dest_coords_lon, _ = get_coords_from_location(route['destination'])

        if start_coords_lat and start_coords_lon and haversine_distance(pump_lat, pump_lon, start_coords_lat, start_coords_lon) <= threshold_km:
            found_matching_routes.append(route['name'])
            continue

        if dest_coords_lat and dest_coords_lon and haversine_distance(pump_lat, pump_lon, dest_coords_lat, dest_coords_lon) <= threshold_km:
            if route['name'] not in found_matching_routes:
                found_matching_routes.append(route['name'])
            continue

        # Kontrola, zda některý z waypointů trasy je blízko pumpy
        for wp_lat, wp_lon in route_waypoints:
            if haversine_distance(pump_lat, pump_lon, wp_lat, wp_lon) <= threshold_km:
                if route['name'] not in found_matching_routes:
                    found_matching_routes.append(route['name'])
                break # Stačí najít jeden waypoint v blízkosti

    if found_matching_routes:
        route_names_str = "\n".join(found_matching_routes)
        messagebox.showinfo(
            "Trasy poblíž pumpy",
            f"Byla nalezena čerpací stanice '{found_station_name}' na adrese '{found_station_address}' (v okolí vámi zadané adresy '{pump_input}').\n\n"
            f"Tyto trasy z vaší databáze procházejí blízko této pumpy:\n\n{route_names_str}",
            parent=user_root
        )
    else:
        messagebox.showinfo(
            "Žádná trasa nalezena",
            f"Byla nalezena čerpací stanice '{found_station_name}' na adrese '{found_station_address}' (v okolí vámi zadané adresy '{pump_input}').\n\n"
            f"Žádná trasa z databáze neprochází blízko této pumpy.",
            parent=user_root
        )


def apply_filters_and_sort(force_fetch=False):
    """
    Aplikuje filtry a řazení na zobrazené trasy.
    Pokud je force_fetch True, načte data z databáze znovu.
    """
    global all_user_routes_cached, current_sort_column, current_sort_order

    if force_fetch:
        all_user_routes_cached = database.get_routes_by_user(current_user_id)
        if all_user_routes_cached is None:
            all_user_routes_cached = [] # Ensure it's a list even if DB call fails
            messagebox.showerror("Chyba databáze", "Nepodařilo se načíst trasy z databáze.", parent=user_root)
            return

    filtered_routes = []
    name_filter = filter_name_entry.get().strip().lower()
    start_filter = filter_start_entry.get().strip().lower()
    destination_filter = filter_destination_entry.get().strip().lower()
    fuel_filter = filter_fuel_var.get() # 'Vše', 'Ano', 'Ne'

    for route in all_user_routes_cached:
        match_name = name_filter in route.get('name', '').lower()
        match_start = start_filter in route.get('start_location', '').lower()
        match_destination = destination_filter in route.get('destination', '').lower()

        match_fuel = True
        if fuel_filter == "Ano":
            match_fuel = route.get('needs_fuel', False) == True
        elif fuel_filter == "Ne":
            match_fuel = route.get('needs_fuel', False) == False

        if match_name and match_start and match_destination and match_fuel:
            filtered_routes.append(route)

    # Sort the filtered results
    def get_sort_key(route):
        if current_sort_column == "distance":
            try:
                # Extract number from "XXX.YY km" string
                return float(route.get('distance', '0').replace(' km', ''))
            except ValueError:
                return 0.0 # Default for invalid distance
        elif current_sort_column == "travel_time":
            return route.get('travel_time', 0)
        elif current_sort_column == "fuel_consumption":
            return route.get('fuel_consumption', 0.0)
        elif current_sort_column == "gas_stations":
            return len(route.get('gas_stations', []))
        elif current_sort_column == "needs_fuel":
            # Sort boolean: False comes before True for 'asc'
            # Python's default sort for booleans is False < True
            return route.get('needs_fuel', False)
        else: # Default to 'name'
            return route.get('name', '').lower()

    # Apply sorting. For needs_fuel, we reverse the reverse logic.
    if current_sort_column == "needs_fuel":
        # If 'asc', we want False (No) first, then True (Yes).
        # Python's sorted(..., reverse=False) puts False before True.
        # So if current_sort_order is "asc", reverse should be False.
        # If current_sort_order is "desc", reverse should be True.
        sort_reverse = (current_sort_order == "desc")
    else:
        sort_reverse = (current_sort_order == "desc")

    filtered_routes.sort(key=get_sort_key, reverse=sort_reverse)


    # Clear current treeview
    for item in user_routes_tree.get_children():
        user_routes_tree.delete(item)

    # Insert filtered and sorted data
    for route in filtered_routes:
        # Ensure values are in the correct order for the Treeview columns
        # Format needs_fuel for display
        needs_fuel_display = "Ano" if route.get('needs_fuel', False) else "Ne"
        num_gas_stations = len(route.get('gas_stations', []))

        user_routes_tree.insert("", "end", values=(
            route.get('name', ''),
            route.get('start_location', ''),
            route.get('destination', ''),
            route.get('distance', ''),
            f"{route.get('travel_time', 0)} s", # Display with 's'
            f"{route.get('fuel_consumption', 0.0):.2f}", # Format fuel consumption to 2 decimal places
            num_gas_stations,
            needs_fuel_display
        ))

def set_sort_and_apply(column, order):
    """Sets the global sort column and order, then applies filters and sorting."""
    global current_sort_column, current_sort_order
    current_sort_column = column
    current_sort_order = order
    apply_filters_and_sort()

def go_back_to_login():
    """Destroys current screen content and returns to login using the stored callback."""
    global user_root, _create_login_widgets_callback, all_user_routes_cached

    # Clear current screen widgets
    for widget in user_root.winfo_children():
        widget.destroy()

    # Reset window size and title
    user_root.geometry("300x200")
    user_root.title("Přihlašovací obrazovka")

    # Clear cached data when logging out
    all_user_routes_cached = []

    # Call the stored callback function to recreate the login UI
    if _create_login_widgets_callback:
        _create_login_widgets_callback()

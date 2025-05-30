import database
import random
from datetime import datetime, timedelta

# Seznam měst pro generování tras
MESTA = [
    "Praha", "Brno", "Ostrava", "Plzeň", "Liberec", "Olomouc", "České Budějovice",
    "Hradec Králové", "Ústí nad Labem", "Pardubice", "Zlín", "Havířov", "Kladno",
    "Most", "Opava", "Frýdek-Místek", "Jihlava", "Karviná", "Teplice", "Chomutov"
]

# Seznam důvodů cest
DUVODY_CEST = [
    "Obchodní jednání", "Služební cesta", "Školení", "Konference", "Pracovní schůzka",
    "Návštěva pobočky", "Audit", "Prezentace", "Workshop", "Konzultace s klientem",
    "Technická podpora", "Instalace zařízení", "Servisní zásah", "Kontrola provozu",
    "Předání dokumentů", "Jednání s dodavateli", "Prohlídka objektu", "Inspekce",
    "Výběrové řízení", "Podpis smlouvy"
]

# Předem definované vzdálenosti mezi městy (přibližné hodnoty v km)
VZDALENOSTI = {
    ("Praha", "Brno"): 205,
    ("Praha", "Ostrava"): 380,
    ("Praha", "Plzeň"): 95,
    ("Praha", "Liberec"): 110,
    ("Praha", "České Budějovice"): 150,
    ("Praha", "Hradec Králové"): 115,
    ("Praha", "Ústí nad Labem"): 90,
    ("Brno", "Ostrava"): 170,
    ("Brno", "Olomouc"): 80,
    ("Ostrava", "Olomouc"): 100,
    ("Plzeň", "České Budějovice"): 140,
    ("Liberec", "Hradec Králové"): 120,
    ("Ústí nad Labem", "Liberec"): 90,
}

def get_distance(mesto1, mesto2):
    """Získá reálnou vzdálenost mezi městy nebo vygeneruje přibližnou."""
    if (mesto1, mesto2) in VZDALENOSTI:
        return VZDALENOSTI[(mesto1, mesto2)]
    if (mesto2, mesto1) in VZDALENOSTI:
        return VZDALENOSTI[(mesto2, mesto1)]
    # Pokud nemáme přesnou vzdálenost, vygenerujeme přibližnou
    # ale s menší variabilitou pro realističtější hodnoty
    base_distance = random.uniform(80, 300)
    return round(base_distance, 1)

def generuj_nahodny_cas(vzdalenost):
    """Generuje realistický čas cesty v sekundách na základě vzdálenosti."""
    # Průměrná rychlost mezi 60-90 km/h
    prumerna_rychlost = random.uniform(60, 90)
    cas_v_hodinach = vzdalenost / prumerna_rychlost
    return int(cas_v_hodinach * 3600)  # převod na sekundy

def generuj_spotrebu(vzdalenost):
    """Generuje spotřebu paliva na základě vzdálenosti (průměrná spotřeba 7L/100km)."""
    zakladni_spotreba = 7.0
    # Přidáme malou náhodnou odchylku (±1L/100km)
    aktualni_spotreba = zakladni_spotreba + random.uniform(-1, 1)
    return round((vzdalenost * aktualni_spotreba) / 100, 1)

def vytvor_testovaci_trasy():
    """Vytvoří 20 testovacích tras pro uživatele s optimalizovanými vzdálenostmi."""
    # Nejprve získáme ID uživatele 'user'
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = 'user'")
    user_result = cursor.fetchone()
    conn.close()

    if not user_result:
        print("Uživatel 'user' nebyl nalezen!")
        return

    user_id = user_result[0]
    print(f"Generuji trasy pro uživatele ID: {user_id}")

    # Seznam pro sledování vygenerovaných tras
    vygenerovane_trasy = []
    celkova_vzdalenost = 0
    cilova_prumerna_vzdalenost = 200  # Cílový průměr km na trasu

    # Generování 16 základních tras (ponecháme 4 pro vyrovnávací)
    for i in range(16):
        # Výběr měst s preferencí pro reálné vzdálenosti
        start = random.choice(MESTA)
        # Preferujeme města, pro která máme reálné vzdálenosti
        mozna_cilova_mesta = [m for m in MESTA if m != start]
        dest = random.choice(mozna_cilova_mesta)
        
        # Získání vzdálenosti
        vzdalenost = get_distance(start, dest)
        cas = generuj_nahodny_cas(vzdalenost)
        spotreba = generuj_spotrebu(vzdalenost)
        
        # Vytvoření trasy
        nazev = f"Trasa {i+1}: {start}-{dest}"
        duvod = random.choice(DUVODY_CEST)
        
        # Přidání trasy do databáze
        success = database.add_route(
            user_id=user_id,
            name=nazev,
            start_location=start,
            destination=dest,
            distance=f"{vzdalenost} km",
            travel_time=cas,
            fuel_consumption=spotreba,
            gas_stations=[],
            needs_fuel=vzdalenost > 200,  # Potřeba tankování pro delší trasy
            waypoints=[],
            trip_purpose=duvod
        )
        
        if success:
            print(f"Vytvořena trasa: {nazev} ({vzdalenost} km)")
            vygenerovane_trasy.append((vzdalenost, nazev))
            celkova_vzdalenost += vzdalenost
        else:
            print(f"Chyba při vytváření trasy: {nazev}")

    # Výpočet průměrné vzdálenosti a odchylky
    prumerna_vzdalenost = celkova_vzdalenost / len(vygenerovane_trasy)
    odchylka = abs(prumerna_vzdalenost - cilova_prumerna_vzdalenost)
    print(f"\nPrůměrná vzdálenost tras: {prumerna_vzdalenost:.1f} km")
    print(f"Odchylka od cíle: {odchylka:.1f} km")

    # Generování vyrovnávacích tras
    for i in range(16, 20):
        if prumerna_vzdalenost < cilova_prumerna_vzdalenost:
            # Potřebujeme delší trasu
            vzdalenost = random.uniform(250, 350)
        else:
            # Potřebujeme kratší trasu
            vzdalenost = random.uniform(50, 150)

        # Najdeme vhodná města s podobnou vzdáleností
        start = "Praha"  # Výchozí bod pro vyrovnávací trasy
        nejlepsi_dest = None
        nejmensi_rozdil = float('inf')
        
        for mesto in MESTA:
            if mesto != start:
                test_vzdalenost = get_distance(start, mesto)
                rozdil = abs(test_vzdalenost - vzdalenost)
                if rozdil < nejmensi_rozdil:
                    nejmensi_rozdil = rozdil
                    nejlepsi_dest = mesto

        vzdalenost = get_distance(start, nejlepsi_dest)
        cas = generuj_nahodny_cas(vzdalenost)
        spotreba = generuj_spotrebu(vzdalenost)
        
        nazev = f"Vyrovnávací trasa {i-15}: {start}-{nejlepsi_dest}"
        duvod = "Vyrovnávací služební cesta"
        
        success = database.add_route(
            user_id=user_id,
            name=nazev,
            start_location=start,
            destination=nejlepsi_dest,
            distance=f"{vzdalenost} km",
            travel_time=cas,
            fuel_consumption=spotreba,
            gas_stations=[],
            needs_fuel=vzdalenost > 200,
            waypoints=[],
            trip_purpose=duvod
        )
        
        if success:
            print(f"Vytvořena vyrovnávací trasa: {nazev} ({vzdalenost} km)")
            celkova_vzdalenost += vzdalenost
        else:
            print(f"Chyba při vytváření vyrovnávací trasy: {nazev}")

    # Závěrečný výpočet průměrné vzdálenosti
    konecna_prumerna_vzdalenost = celkova_vzdalenost / 20
    print(f"\nKonečná průměrná vzdálenost všech tras: {konecna_prumerna_vzdalenost:.1f} km")

if __name__ == "__main__":
    print("Začínám generovat testovací trasy...")
    vytvor_testovaci_trasy()
    print("Generování tras dokončeno.") 
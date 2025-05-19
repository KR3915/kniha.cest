import tkinter as tk
import sys

def print_number():
    print("123")

def show_page2():
    """Show page 2 and hide page 1."""
    page1.pack_forget()  # Hide page 1
    page2.pack()        # Show page 2

def show_page1():
    """Show page 1 and hide page 2."""
    page2.pack_forget()  # Hide page 2
    page1.pack()        # Show page 1

if __name__ == "__main__":
    username = "Neznámý uživatel"  # Defaultní hodnota, pokud není jméno předáno
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Uživatelské jméno přihlášeného uživatele: {username}")

    # Create the main window
    root = tk.Tk()
    root.title(f"Uživatelská obrazovka pro {username}")  # Set the title with username
    root.geometry("300x400")  # Increased window size

    # Page 1
    page1 = tk.Frame(root)
    page1.pack(pady=20)  # Add some padding

    welcome_label = tk.Label(page1, text=f"Vítejte, {username}!", font=("Arial", 16))
    welcome_label.pack(pady=10)

    nastavit_trasu_button = tk.Button(page1, text="Nastavit trasu", command=show_page2, padx=20, pady=10)
    nastavit_trasu_button.pack()

    # Page 2
    page2 = tk.Frame(root)

    zpet_button = tk.Button(page2, text="Zpět na dashboard", command=show_page1, padx=20, pady=10)
    zpet_button.pack(pady=20)

    number_button = tk.Button(page2, text="Vytisknout číslo", command=print_number, padx=20, pady=10)
    number_button.pack()

    # Initially show page 1
    show_page1()

    # Run the Tkinter event loop
    root.mainloop()
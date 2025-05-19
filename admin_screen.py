import tkinter as tk
from tkinter import ttk
def create_page(parent, page_name):
    page_frame = ttk.Frame(parent)
    page_frame.columnconfigure(0, weight=1)  # Ensure buttons can expand

    label = ttk.Label(page_frame, text=f"This is {page_name}", font=("TkDefaultFont", 16))
    label.grid(row=0, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

    button1 = ttk.Button(page_frame, text=f"{page_name} Button 1", command=lambda: print(f"{page_name} Button 1 clicked!"))
    button1.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    button2 = ttk.Button(page_frame, text=f"{page_name} Button 2", command=lambda: print(f"{page_name} Button 2 clicked!"))
    button2.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    return page_frame

def show_page(page):

    page.tkraise()

def main():
    window = tk.Tk()
    window.title("admin panel")
    window.geometry("400x300")  # Set initial window size

    # Create a main container frame to hold all pages
    main_container = ttk.Frame(window)
    main_container.pack(fill="both", expand=True)  # Use pack for main container

    # Create the pages
    page1 = create_page(main_container, "Page 1")
    page2 = create_page(main_container, "Page 2")

    # Create the initial page with two buttons
    initial_page = ttk.Frame(main_container)
    initial_page.columnconfigure(0, weight=1)  # Make columns expandable
    initial_page.columnconfigure(1, weight=1)

    label_initial = ttk.Label(initial_page, text="admin panel", font=("TkDefaultFont", 18))
    label_initial.grid(row=0, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

    button_page1 = ttk.Button(initial_page, text="Go to Page 1", command=lambda: show_page(page1))
    button_page1.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    button_page2 = ttk.Button(initial_page, text="Go to Page 2", command=lambda: show_page(page2))
    button_page2.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    # Place all pages in the container.  Only one will be visible at a time.
    initial_page.grid(row=0, column=0, sticky="nsew")
    page1.grid(row=0, column=0, sticky="nsew")
    page2.grid(row=0, column=0, sticky="nsew")

    # Make the container frame resizable, so the pages can fill it.
    main_container.grid_rowconfigure(0, weight=1)
    main_container.grid_columnconfigure(0, weight=1)
    
    # Show the initial page first
    show_page(initial_page)

    window.mainloop()

if __name__ == "__main__":
    main()

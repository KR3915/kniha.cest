import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any
from config import WINDOW_SIZE
from database import db
from ui.login import LoginFrame
from ui.route_manager import RouteManager
from ui.map_view import MapView, RouteDetails

class Application:
    """Main application class."""
    def __init__(self):
        # Initialize database
        db.init_db()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Route Planner")
        self.root.geometry(WINDOW_SIZE)
        
        # Initialize state
        self.current_user = None
        self.current_user_id = None
        self.is_admin = False
        
        # Show login screen
        self._show_login()
        
    def run(self):
        """Start the application."""
        self.root.mainloop()
        
    def _show_login(self):
        """Show the login screen."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Show login frame
        LoginFrame(self.root, self._handle_login).pack(expand=True, fill=tk.BOTH)
        
    def _handle_login(self, username: str, user_id: int, is_admin: bool):
        """Handle successful login."""
        self.current_user = username
        self.current_user_id = user_id
        self.is_admin = is_admin
        
        # Show main interface
        self._show_main_interface()
        
    def _show_main_interface(self):
        """Show the main application interface."""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Update window
        self.root.title(f"Route Planner - {self.current_user}")
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(True, True)
        
        # Create main container with padding
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Create left panel (route manager) - 40% width
        left_panel = ctk.CTkFrame(main_container, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_panel.pack_propagate(False)  # Prevent shrinking
        
        # Add route manager
        self.route_manager = RouteManager(
            left_panel,
            self.current_user_id,
            self._handle_route_select
        )
        self.route_manager.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Create right panel - 60% width
        right_panel = ctk.CTkFrame(main_container, width=600)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        right_panel.pack_propagate(False)  # Prevent shrinking
        
        # Add map view (70% height)
        map_container = ctk.CTkFrame(right_panel)
        map_container.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.map_view = MapView(map_container)
        self.map_view.pack(expand=True, fill=tk.BOTH)
        
        # Add route details (30% height)
        details_container = ctk.CTkFrame(right_panel, height=200)
        details_container.pack(fill=tk.X, pady=(5, 0))
        details_container.pack_propagate(False)  # Prevent shrinking
        
        self.route_details = RouteDetails(details_container)
        self.route_details.pack(fill=tk.BOTH, expand=True)
        
        # Add logout button
        logout_btn = ctk.CTkButton(
            right_panel,
            text="Logout",
            command=self._handle_logout,
            width=120
        )
        logout_btn.pack(pady=10)
        
    def _handle_route_select(self, route_data: Dict[str, Any]):
        """Handle route selection."""
        # Update route details
        self.route_details.update_details(route_data)
        
        # Update map
        if route_data and route_data.get('route_geometry'):
            geometry = route_data['route_geometry']
            if isinstance(geometry, str):
                import json
                geometry = json.loads(geometry)
                
            gas_stations = route_data.get('gas_stations', [])
            if isinstance(gas_stations, str):
                gas_stations = json.loads(gas_stations)
                
            self.map_view.display_route(
                geometry,
                (geometry[0]['latitude'], geometry[0]['longitude']),
                (geometry[-1]['latitude'], geometry[-1]['longitude']),
                gas_stations
            )
            
    def _handle_logout(self):
        """Handle logout."""
        self.current_user = None
        self.current_user_id = None
        self.is_admin = False
        self._show_login()

if __name__ == "__main__":
    app = Application()
    app.run() 
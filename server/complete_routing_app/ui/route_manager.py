import tkinter as tk
import customtkinter as ctk
from typing import Any, Callable, Dict, List
from .base import (
    BaseFrame,
    StyledButton,
    StyledEntry,
    StyledLabel,
    ScrollableFrame,
    MessageBox,
    COLORS,
    FONTS
)
from database import db
from tomtom_api import api

class RouteManager(BaseFrame):
    """Route management interface."""
    def __init__(
        self,
        master: Any,
        user_id: int,
        on_route_select: Callable[[Dict[str, Any]], None]
    ):
        super().__init__(master)
        self.user_id = user_id
        self.on_route_select = on_route_select
        
        self._create_widgets()
        self._show_initial_message()
        
    def _create_widgets(self):
        """Create route manager widgets."""
        # Main container with padding
        self.main_container = BaseFrame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header = BaseFrame(self.main_container)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        StyledLabel(
            header,
            text="Your Routes",
            font_style="subheading"
        ).pack(side=tk.LEFT)
        
        # Action buttons
        actions = BaseFrame(header)
        actions.pack(side=tk.RIGHT)
        
        StyledButton(
            actions,
            text="New Route",
            command=self._show_route_form,
            color="primary",
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        StyledButton(
            actions,
            text="Refresh",
            command=self.load_routes,
            color="info",
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        # Routes list
        self.routes_container = ScrollableFrame(self.main_container)
        self.routes_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create routes list
        self.routes_list = tk.Listbox(
            self.routes_container,
            bg=COLORS['white'],
            fg=COLORS['dark'],
            selectmode=tk.SINGLE,
            font=FONTS['default'],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=COLORS['primary'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['white']
        )
        self.routes_list.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.routes_list.bind('<<ListboxSelect>>', self._on_route_select)
        
    def _show_initial_message(self):
        """Show initial message when no routes exist."""
        self.initial_message = StyledLabel(
            self.routes_container,
            text="No routes yet. Click 'New Route' to create one!",
            font_style="default"
        )
        self.initial_message.pack(expand=True)
        
    def _hide_initial_message(self):
        """Hide the initial message."""
        if hasattr(self, 'initial_message'):
            self.initial_message.pack_forget()
            
    def load_routes(self):
        """Load and display user routes."""
        # Clear existing items
        self.routes_list.delete(0, tk.END)
        
        # Get routes from database
        routes = db.get_user_routes(self.user_id)
        
        # Show/hide no routes message
        if not routes:
            self.routes_list.pack_forget()
            self._show_initial_message()
        else:
            self._hide_initial_message()
            self.routes_list.pack(fill=tk.BOTH, expand=True)
            
            # Add routes to list
            for route in routes:
                self.routes_list.insert(
                    tk.END,
                    f"{route['name']} ({route['start_location']} → {route['destination']})"
                )
                # Store route data as item attribute
                self.routes_list.itemconfig(
                    tk.END,
                    {'route_data': route}
                )
                
    def _on_route_select(self, event):
        """Handle route selection."""
        selection = self.routes_list.curselection()
        if not selection:
            return
            
        # Get selected route data
        route_data = self.routes_list.itemcget(selection[0], 'route_data')
        if route_data and self.on_route_select:
            self.on_route_select(route_data)
            
    def _show_route_form(self):
        """Show route creation form."""
        RouteForm(self, self.user_id, self.load_routes)

class RouteForm(ctk.CTkToplevel):
    """Route creation/edit form."""
    def __init__(
        self,
        master: Any,
        user_id: int,
        on_save: Callable,
        route_data: Dict[str, Any] = None
    ):
        super().__init__(master)
        
        self.user_id = user_id
        self.on_save = on_save
        self.route_data = route_data
        
        # Window setup
        self.title("New Route" if not route_data else "Edit Route")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Center on parent
        x = master.winfo_x() + (master.winfo_width() - 500) // 2
        y = master.winfo_y() + (master.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create form widgets."""
        # Main container
        container = BaseFrame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Form title
        StyledLabel(
            container,
            text="Route Details",
            font_style="heading"
        ).pack(pady=(0, 20))
        
        # Form fields
        self.fields = {}
        
        # Route name
        name_container = BaseFrame(container)
        name_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            name_container,
            text="Route Name:",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.fields['name'] = StyledEntry(
            name_container,
            placeholder="Enter route name"
        )
        self.fields['name'].pack(fill=tk.X, pady=(5, 0))
        
        # Start location
        start_container = BaseFrame(container)
        start_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            start_container,
            text="Start Location:",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.fields['start'] = StyledEntry(
            start_container,
            placeholder="Enter start location"
        )
        self.fields['start'].pack(fill=tk.X, pady=(5, 0))
        
        # Destination
        dest_container = BaseFrame(container)
        dest_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            dest_container,
            text="Destination:",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.fields['destination'] = StyledEntry(
            dest_container,
            placeholder="Enter destination"
        )
        self.fields['destination'].pack(fill=tk.X, pady=(5, 0))
        
        # Options
        options_container = BaseFrame(container)
        options_container.pack(fill=tk.X, pady=20)
        
        self.fields['traffic'] = tk.BooleanVar(value=False)
        traffic_check = ctk.CTkCheckBox(
            options_container,
            text="Enable Traffic",
            variable=self.fields['traffic'],
            font=FONTS['default'],
            text_color=COLORS['dark']
        )
        traffic_check.pack(side=tk.LEFT, padx=5)
        
        self.fields['tolls'] = tk.BooleanVar(value=False)
        tolls_check = ctk.CTkCheckBox(
            options_container,
            text="Avoid Tolls",
            variable=self.fields['tolls'],
            font=FONTS['default'],
            text_color=COLORS['dark']
        )
        tolls_check.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_container = BaseFrame(container)
        button_container.pack(fill=tk.X, pady=(20, 0))
        
        StyledButton(
            button_container,
            text="Cancel",
            command=self.destroy,
            color="secondary",
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        StyledButton(
            button_container,
            text="Save",
            command=self._save_route,
            width=100
        ).pack(side=tk.RIGHT, padx=5)
        
        # Fill fields if editing
        if self.route_data:
            self.fields['name'].insert(0, self.route_data['name'])
            self.fields['start'].insert(0, self.route_data['start_location'])
            self.fields['destination'].insert(0, self.route_data['destination'])
            self.fields['traffic'].set(self.route_data.get('traffic_enabled', False))
            self.fields['tolls'].set(self.route_data.get('avoid_tolls', False))
            
    def _save_route(self):
        """Save route data."""
        # Validate fields
        name = self.fields['name'].get().strip()
        start = self.fields['start'].get().strip()
        destination = self.fields['destination'].get().strip()
        
        if not all([name, start, destination]):
            MessageBox(
                "Error",
                "Please fill in all required fields",
                type_="danger",
                parent=self
            )
            return
            
        # Prepare route data
        route_data = {
            'name': name,
            'start_location': start,
            'destination': destination,
            'traffic_enabled': self.fields['traffic'].get(),
            'avoid_tolls': self.fields['tolls'].get()
        }
        
        # Save to database
        if self.route_data:
            success = db.update_route(
                self.route_data['id'],
                self.user_id,
                route_data
            )
        else:
            success = db.add_route(self.user_id, route_data)
            
        if success:
            self.destroy()
            self.on_save()
        else:
            MessageBox(
                "Error",
                "Failed to save route",
                type_="danger",
                parent=self
            ) 
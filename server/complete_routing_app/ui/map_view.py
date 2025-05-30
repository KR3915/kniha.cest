import tkinter as tk
import customtkinter as ctk
from typing import Any, Dict, List, Tuple
import folium
import webbrowser
import os
from .base import (
    BaseFrame,
    StyledButton,
    StyledLabel,
    COLORS,
    FONTS
)

class MapView(BaseFrame):
    """Interactive map view using Folium."""
    def __init__(self, master: Any):
        super().__init__(master)
        
        # Initialize state
        self.current_route = None
        self.current_stations = []
        self.map_file = os.path.join('.cache', 'route_map.html')
        os.makedirs('.cache', exist_ok=True)
        
        self._create_widgets()
        self._show_initial_message()
        
    def _create_widgets(self):
        """Create map view widgets."""
        # Main container with padding
        self.main_container = BaseFrame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar
        self.toolbar = BaseFrame(self.main_container)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Add toolbar buttons
        StyledButton(
            self.toolbar,
            text="Zoom In",
            command=self._zoom_in,
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        StyledButton(
            self.toolbar,
            text="Zoom Out",
            command=self._zoom_out,
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        StyledButton(
            self.toolbar,
            text="Center Map",
            command=self._center_map,
            width=100
        ).pack(side=tk.LEFT, padx=5)
        
        # Map container
        self.map_container = BaseFrame(self.main_container)
        self.map_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Browser button
        StyledButton(
            self.map_container,
            text="Open in Browser",
            command=self._open_in_browser,
            color="secondary",
            width=120
        ).pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)
        
    def _show_initial_message(self):
        """Show initial message when no route is selected."""
        self.initial_message = StyledLabel(
            self.map_container,
            text="Select a route or create a new one to view the map",
            font_style="subheading"
        )
        self.initial_message.pack(expand=True)
        
    def _hide_initial_message(self):
        """Hide the initial message."""
        if hasattr(self, 'initial_message'):
            self.initial_message.pack_forget()
            
    def display_route(
        self,
        route_points: List[Dict[str, float]],
        start_location: Tuple[float, float],
        end_location: Tuple[float, float],
        gas_stations: List[Dict[str, Any]] = None
    ):
        """Display a route on the map."""
        self._hide_initial_message()
        self.current_route = route_points
        self.current_stations = gas_stations or []
        
        # Create a new map centered on the route
        center_lat = (start_location[0] + end_location[0]) / 2
        center_lon = (start_location[1] + end_location[1]) / 2
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles="OpenStreetMap"
        )
        
        # Add route line
        route_coords = [[p['latitude'], p['longitude']] for p in route_points]
        folium.PolyLine(
            route_coords,
            weight=4,
            color=COLORS['primary'].lstrip('#'),
            opacity=0.8
        ).add_to(m)
        
        # Add start marker
        folium.Marker(
            [start_location[0], start_location[1]],
            popup='Start',
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
        # Add end marker
        folium.Marker(
            [end_location[0], end_location[1]],
            popup='Destination',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add gas station markers
        if gas_stations:
            for station in gas_stations:
                folium.Marker(
                    [station['latitude'], station['longitude']],
                    popup=f"{station['name']}<br>{station['address']}",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(m)
        
        # Save map to file
        m.save(self.map_file)
        
        # Open in default browser
        self._open_in_browser()
        
    def _zoom_in(self):
        """Zoom in on the map."""
        if os.path.exists(self.map_file):
            self._open_in_browser()
            
    def _zoom_out(self):
        """Zoom out on the map."""
        if os.path.exists(self.map_file):
            self._open_in_browser()
            
    def _center_map(self):
        """Center the map on the current route."""
        if self.current_route:
            self.display_route(
                self.current_route,
                (self.current_route[0]['latitude'], self.current_route[0]['longitude']),
                (self.current_route[-1]['latitude'], self.current_route[-1]['longitude']),
                self.current_stations
            )
            
    def _open_in_browser(self):
        """Open the map in the default web browser."""
        if os.path.exists(self.map_file):
            webbrowser.open(f'file://{os.path.abspath(self.map_file)}')
            
    def clear(self):
        """Clear the current map."""
        self.current_route = None
        self.current_stations = []
        if os.path.exists(self.map_file):
            try:
                os.remove(self.map_file)
            except Exception as e:
                print(f"Error clearing map: {e}")
        self._show_initial_message()

class RouteDetails(BaseFrame):
    """Route details panel."""
    def __init__(self, master: Any):
        super().__init__(master)
        self._create_widgets()
        
    def _create_widgets(self):
        """Create route details widgets."""
        # Title
        StyledLabel(
            self,
            text="Route Details",
            font_style="subheading"
        ).pack(padx=10, pady=(10, 5))
        
        # Details container
        self.details_container = BaseFrame(self)
        self.details_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Initial message
        self.initial_message = StyledLabel(
            self.details_container,
            text="Select a route to view details",
            font_style="default"
        )
        self.initial_message.pack(expand=True)
        
        # Create labels for details
        self.labels = {}
        for field in ['Distance', 'Travel Time', 'Fuel Consumption', 'Gas Stations']:
            container = ctk.CTkFrame(self.details_container, fg_color="transparent")
            container.pack(fill=tk.X, pady=2)
            
            StyledLabel(
                container,
                text=f"{field}:",
                font_style="small"
            ).pack(side=tk.LEFT)
            
            self.labels[field.lower()] = StyledLabel(
                container,
                text="",
                font_style="default"
            )
            self.labels[field.lower()].pack(side=tk.RIGHT)
            
        # Hide details initially
        self.details_container.pack_forget()
        
    def update_details(self, route_data: Dict[str, Any]):
        """Update route details display."""
        if not route_data:
            self.details_container.pack_forget()
            self.initial_message.pack(expand=True)
            return
            
        self.initial_message.pack_forget()
        self.details_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Update labels
        self.labels['distance'].configure(
            text=f"{route_data['distance']:.1f} km"
        )
        self.labels['travel time'].configure(
            text=self._format_duration(route_data['travel_time'])
        )
        self.labels['fuel consumption'].configure(
            text=f"{route_data['fuel_consumption']:.1f}L"
        )
        
        gas_stations = route_data.get('gas_stations', [])
        if isinstance(gas_stations, str):
            import json
            gas_stations = json.loads(gas_stations)
        self.labels['gas stations'].configure(
            text=str(len(gas_stations))
        )
        
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to hours and minutes."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" 
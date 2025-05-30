import requests
from typing import Dict, List, Optional, Any, Tuple
from config import (
    TOMTOM_API_KEY, BASE_URL, SEARCH_API_VERSION,
    ROUTING_API_VERSION, DEFAULT_SEARCH_RADIUS, MAX_STATIONS
)

class TomTomAPI:
    def __init__(self):
        self.api_key = TOMTOM_API_KEY
        self.base_url = BASE_URL
        self.search_version = SEARCH_API_VERSION
        self.routing_version = ROUTING_API_VERSION

    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make an HTTP request to the TomTom API."""
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None

    def geocode(self, location: str) -> Optional[Dict[float, float]]:
        """Convert a location string to coordinates."""
        url = f"{self.base_url}/search/{self.search_version}/geocode/{location}.json"
        params = {
            'key': self.api_key,
            'limit': 1
        }

        data = self._make_request(url, params)
        if data and data.get('results'):
            position = data['results'][0]['position']
            return {
                'lat': position['lat'],
                'lon': position['lon']
            }
        return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """Convert coordinates to a location address."""
        url = f"{self.base_url}/search/{self.search_version}/reverseGeocode/{lat},{lon}.json"
        params = {
            'key': self.api_key
        }

        data = self._make_request(url, params)
        if data and data.get('addresses'):
            address = data['addresses'][0]['address']
            return address.get('freeformAddress', f"{lat},{lon}")
        return None

    def calculate_route(
        self,
        start_coords: Dict[str, float],
        end_coords: Dict[str, float],
        waypoints: List[Dict[str, float]] = None,
        traffic: bool = False,
        avoid_tolls: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Calculate a route between two points with optional waypoints."""
        # Build coordinates string
        coords = [f"{start_coords['lat']},{start_coords['lon']}"]
        if waypoints:
            for point in waypoints:
                coords.append(f"{point['lat']},{point['lon']}")
        coords.append(f"{end_coords['lat']},{end_coords['lon']}")

        url = f"{self.base_url}/routing/{self.routing_version}/calculateRoute/{':'.join(coords)}/json"
        
        params = {
            'key': self.api_key,
            'traffic': str(traffic).lower(),
            'computeBestOrder': 'true',
            'routeType': 'fastest',
            'travelMode': 'car',
            'avoid': 'unpavedRoads',
            'computeTravelTimeFor': 'all',
            'returnGeometryPolyline': 'true'
        }

        if avoid_tolls:
            params['avoid'] = f"{params['avoid']},tollRoads"

        data = self._make_request(url, params)
        if data and data.get('routes'):
            route = data['routes'][0]
            return {
                'summary': route['summary'],
                'legs': route['legs'],
                'geometry': route.get('legs', [{}])[0].get('points', []),
                'polyline': route.get('geometry', '')
            }
        return None

    def find_gas_stations(
        self,
        lat: float,
        lon: float,
        radius: int = DEFAULT_SEARCH_RADIUS,
        limit: int = MAX_STATIONS
    ) -> List[Dict[str, Any]]:
        """Find gas stations near a point."""
        url = f"{self.base_url}/search/{self.search_version}/categorySearch/petrol-station.json"
        params = {
            'key': self.api_key,
            'lat': lat,
            'lon': lon,
            'radius': radius,
            'limit': limit
        }

        data = self._make_request(url, params)
        stations = []
        if data and data.get('results'):
            for result in data['results']:
                station = {
                    'station_id': result['id'],
                    'name': result['poi']['name'],
                    'brand': result['poi'].get('brands', [{}])[0].get('name', 'Unknown'),
                    'latitude': result['position']['lat'],
                    'longitude': result['position']['lon'],
                    'address': result['address'].get('freeformAddress', ''),
                    'distance': result.get('dist', 0)
                }
                stations.append(station)
        return stations

    def find_gas_stations_along_route(
        self,
        route_geometry: List[Dict[str, float]],
        radius: int = DEFAULT_SEARCH_RADIUS,
        max_stations: int = MAX_STATIONS
    ) -> List[Dict[str, Any]]:
        """Find gas stations along a route."""
        stations = []
        seen_station_ids = set()

        # Sample points along the route
        sample_points = self._sample_route_points(route_geometry)

        for point in sample_points:
            point_stations = self.find_gas_stations(
                point['latitude'],
                point['longitude'],
                radius=radius,
                limit=max_stations
            )

            for station in point_stations:
                if station['station_id'] not in seen_station_ids:
                    seen_station_ids.add(station['station_id'])
                    stations.append(station)

        # Sort by distance and limit the number of stations
        stations.sort(key=lambda x: x['distance'])
        return stations[:max_stations]

    def _sample_route_points(
        self,
        route_geometry: List[Dict[str, float]],
        sample_count: int = 5
    ) -> List[Dict[str, float]]:
        """Sample evenly spaced points along the route."""
        if not route_geometry or len(route_geometry) < 2:
            return []

        points = []
        total_points = len(route_geometry)
        step = max(1, total_points // sample_count)

        for i in range(0, total_points, step):
            if len(points) < sample_count:
                points.append(route_geometry[i])

        # Always include the last point
        if route_geometry[-1] not in points:
            points.append(route_geometry[-1])

        return points

    def calculate_matrix(
        self,
        origins: List[Dict[str, float]],
        destinations: List[Dict[str, float]]
    ) -> Optional[List[List[Dict[str, int]]]]:
        """Calculate a matrix of routes between multiple origins and destinations."""
        url = f"{self.base_url}/routing/{self.routing_version}/matrix/json"
        
        # Prepare origins and destinations in the required format
        origins_list = [{'point': f"{o['lat']},{o['lon']}"} for o in origins]
        destinations_list = [{'point': f"{d['lat']},{d['lon']}"} for d in destinations]

        params = {
            'key': self.api_key,
            'routeType': 'fastest',
            'travelMode': 'car',
            'traffic': 'false'
        }

        data = {
            'origins': origins_list,
            'destinations': destinations_list
        }

        try:
            response = requests.post(url, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result and 'data' in result:
                return result['data']
            return None
        except requests.exceptions.RequestException as e:
            print(f"Matrix calculation error: {e}")
            return None

# Create a global API instance
api = TomTomAPI() 
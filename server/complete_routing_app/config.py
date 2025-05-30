import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
TOMTOM_API_KEY = 'Guh742xz9ZSxx11iki85pe5bvprH9xL9'  # Direct API key configuration
BASE_URL = "https://api.tomtom.com"
SEARCH_API_VERSION = "2"
ROUTING_API_VERSION = "1"

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'routing_app.db')
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'kniha_data',
    'user': 'kniha_user',
    'password': '4T7*hT4cB'
}

# Application Settings
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
CACHE_DURATION_MINUTES = int(os.getenv('CACHE_DURATION_MINUTES', '60'))
DEFAULT_FUEL_CONSUMPTION = float(os.getenv('DEFAULT_FUEL_CONSUMPTION', '7.0'))

# UI Configuration
WINDOW_SIZE = "1024x768"
PADDING = 10
COLORS = {
    'primary': '#2196F3',
    'secondary': '#FFC107',
    'success': '#4CAF50',
    'danger': '#F44336',
    'warning': '#FF9800',
    'info': '#00BCD4',
    'light': '#F5F5F5',
    'dark': '#212121',
    'white': '#FFFFFF',
    'black': '#000000',
}

FONTS = {
    'default': ('Segoe UI', 12),
    'title': ('Segoe UI', 24, 'bold'),
    'subtitle': ('Segoe UI', 18, 'bold'),
    'button': ('Segoe UI', 12),
    'small': ('Segoe UI', 10),
}

# Route Configuration
DEFAULT_SEARCH_RADIUS = 5000  # meters
MAX_STATIONS = 10
MIN_FUEL_THRESHOLD = 50  # km
ROUTE_COLORS = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']

# Map Configuration
DEFAULT_ZOOM = 13
MAP_PROVIDER = 'TomTom'
CACHE_DIR = '.cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Error Messages
ERRORS = {
    'api_key_missing': 'TomTom API key is missing. Please set it in the .env file.',
    'network_error': 'Network error occurred. Please check your internet connection.',
    'route_not_found': 'Could not calculate route between the specified locations.',
    'location_not_found': 'Could not find the specified location.',
    'database_error': 'Database error occurred.',
    'invalid_credentials': 'Invalid username or password.',
    'username_exists': 'Username already exists.',
    'empty_fields': 'Please fill in all required fields.',
} 
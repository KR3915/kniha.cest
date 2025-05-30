# Route Planner

A modern route planning application with TomTom API integration, featuring route management, gas station search, and interactive maps.

## Features

- User authentication and registration
- Route creation and management
- Real-time traffic information
- Gas station search along routes
- Interactive map visualization
- Route details with distance, time, and fuel estimates
- Modern and responsive UI using CustomTkinter

## Requirements

- Python 3.8 or higher
- Required packages (see requirements.txt)
- TomTom API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd route-planner
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your TomTom API key:
```
TOMTOM_API_KEY=your_api_key_here
DATABASE_PATH=routing_app.db
DEFAULT_LANGUAGE=en
CACHE_DURATION_MINUTES=60
DEFAULT_FUEL_CONSUMPTION=7.0
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Register a new account or log in with existing credentials.

3. Create a new route:
   - Click "New Route"
   - Enter route name, start location, and destination
   - Enable/disable traffic and toll avoidance options
   - Click "Save Route"

4. View route details:
   - Select a route from the list
   - View route information in the details panel
   - See the route and gas stations on the map

5. Manage routes:
   - Delete routes using the "Delete" button
   - Refresh the route list using the "Refresh" button
   - View route details by selecting a route

## Development

The application is structured as follows:

```
complete_routing_app/
├── __init__.py
├── config.py
├── database.py
├── main.py
├── tomtom_api.py
├── requirements.txt
├── README.md
└── ui/
    ├── __init__.py
    ├── base.py
    ├── login.py
    ├── map_view.py
    └── route_manager.py
```

- `config.py`: Configuration settings and constants
- `database.py`: SQLite database management
- `tomtom_api.py`: TomTom API integration
- `main.py`: Main application entry point
- `ui/`: User interface components

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TomTom for providing the mapping and routing APIs
- CustomTkinter for the modern UI components
- Folium for map visualization 
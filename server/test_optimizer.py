from datetime import datetime
import database
from fuel_optimizer import find_optimal_solution, calculate_fuel_consumption
from decimal import Decimal

def format_route_action(action, current_tank):
    """Format a route action for display."""
    if action.action_type == 'drive':
        distance = float(str(action.details['distance']).replace(' km', '').replace(',', '.'))
        return f"Drive: {action.details['start_location']} -> {action.details['destination']} ({distance:.1f}km, {float(action.amount):.3f}L)    Tank: {float(current_tank):.3f}L"
    else:
        return f"Refuel {float(action.amount):.3f}L at {action.details['location']}    Tank: {float(current_tank):.3f}L"

def test_route_combinations():
    """Test how the algorithm combines routes to reach target fuel level."""
    # Get routes from database
    user_id = 1  # Assuming user ID 1
    available_routes = database.get_all_routes(user_id)
    
    # Print available routes and their consumptions
    print("\nDostupné trasy:")
    print("-" * 80)
    print(f"{'Název':<30} {'Vzdálenost':<15} {'Spotřeba':<15}")
    print("-" * 80)
    
    for route in available_routes:
        try:
            distance = float(str(route['distance']).replace(' km', '').replace(',', '.'))
            consumption = calculate_fuel_consumption(distance)
            print(f"{route['name']:<30} {distance:>8.1f} km    {float(consumption):>8.3f} L")
        except (ValueError, TypeError):
            continue
    
    # Test case from the error
    initial_tank = 61.545
    target_tank = 30.000
    start_date = datetime.now()
    
    print("\nTest případu:")
    print(f"Počáteční stav: {initial_tank:.3f}L")
    print(f"Cílový stav: {target_tank:.3f}L")
    print(f"Potřebná spotřeba: {initial_tank - target_tank:.3f}L")
    
    # Find solution
    solution = find_optimal_solution(
        initial_tank=initial_tank,
        target_tank=target_tank,
        start_date=start_date,
        available_routes=available_routes,
        refueling_data={},
        max_iterations=100000
    )
    
    if solution:
        print("\nNalezené řešení:")
        print("-" * 80)
        current_tank = Decimal(str(initial_tank))
        total_consumption = Decimal('0')
        
        for action in solution:
            if action.action_type == 'drive':
                current_tank -= action.amount
                total_consumption += action.amount
                print(format_route_action(action, current_tank))
        
        print("-" * 80)
        print(f"Celková spotřeba: {float(total_consumption):.3f}L")
        print(f"Konečný stav nádrže: {float(current_tank):.3f}L")
        print(f"Cílový stav nádrže: {target_tank:.3f}L")
        print(f"Rozdíl od cíle: {float(abs(current_tank - Decimal(str(target_tank)))):.3f}L")
    else:
        print("\nŘešení nebylo nalezeno!")

if __name__ == "__main__":
    test_route_combinations() 
import random
from datetime import datetime, timedelta
from decimal import Decimal
import statistics
from fuel_optimizer import integrate_with_ui, calculate_fuel_consumption, parse_distance

def generate_test_routes():
    """Generate a set of test routes with varying distances."""
    routes = []
    
    # Add routes with different distances for better flexibility
    distances = [10, 20, 35, 50, 70, 100]  # Different distances in km
    for i, distance in enumerate(distances):
        # Calculate consumption using the same function as the optimizer
        distance_dec = Decimal(str(distance))
        consumption = calculate_fuel_consumption(distance_dec)
        
        routes.append({
            'id': i + 1,
            'name': f'Testovací trasa {distance}km',
            'start_location': 'Start',
            'destination': 'Cíl',
            'distance': f"{distance} km",
            'travel_time': distance * 2,  # Approximate travel time
            'fuel_consumption': float(consumption),  # Use the same calculation as optimizer
            'needs_fuel': False,
            'trip_purpose': 'Test'
        })
    
    return routes

def generate_random_test_case():
    """Generate random test case with realistic values."""
    # Random initial tank level between 20 and 85 liters
    initial_tank = round(random.uniform(20, 85), 3)
    
    # Random final tank level between 15 and initial_tank - 5
    # Ensure we always need to reduce fuel level
    final_tank = round(random.uniform(15, max(15, initial_tank - 5)), 3)
    
    # Random number of refueling events (0-3)
    num_refueling = random.randint(0, 3)
    
    # Generate refueling data
    refueling_data = {}
    total_refueled = 0
    
    # Get a random date in May 2025
    base_date = datetime(2025, 5, 1)
    
    for _ in range(num_refueling):
        # Random date in May 2025
        days_offset = random.randint(1, 28)
        refuel_date = base_date + timedelta(days=days_offset)
        
        # Random amount between 5 and 20 liters
        amount = round(random.uniform(5, 20), 3)
        total_refueled += amount
        
        if refuel_date.date() not in refueling_data:
            refueling_data[refuel_date.date()] = []
        
        refueling_data[refuel_date.date()].append({
            "amount": amount,
            "location": f"Test Station {days_offset}"
        })
    
    return {
        "initial_tank": initial_tank,
        "final_tank": final_tank,
        "refueling_data": refueling_data,
        "total_refueled": total_refueled
    }

def run_algorithm_tests(num_tests=10):
    """Run multiple tests and analyze results."""
    deviations = []
    successful_tests = 0
    failed_tests = 0
    
    print("Starting algorithm accuracy analysis...")
    print("-" * 80)
    print(f"{'Test #':<8} {'Initial':<10} {'Final':<10} {'Refueled':<10} {'Achieved':<10} {'Deviation':<10}")
    print("-" * 80)
    
    # Generate test routes once
    available_routes = generate_test_routes()
    
    for test_num in range(1, num_tests + 1):
        # Generate test case
        test_case = generate_random_test_case()
        
        # Run algorithm
        result = integrate_with_ui(
            initial_tank=test_case["initial_tank"],
            target_tank=test_case["final_tank"],
            start_date=datetime(2025, 5, 1),
            refueling_data=test_case["refueling_data"]
        )
        
        if result and result.get('success'):
            successful_tests += 1
            # Get statistics from result
            final_tank_achieved = result['statistics']['final_tank']
            target_tank = test_case["final_tank"]
            
            # Calculate deviation percentage
            deviation = abs(final_tank_achieved - target_tank) / target_tank * 100
            deviations.append(deviation)
            
            print(f"{test_num:<8} {test_case['initial_tank']:<10.3f} {target_tank:<10.3f} "
                  f"{test_case['total_refueled']:<10.3f} {final_tank_achieved:<10.3f} "
                  f"{deviation:<10.2f}%")
        else:
            failed_tests += 1
            error_msg = result.get('error', 'Unknown error') if result else 'No result'
            print(f"{test_num:<8} {test_case['initial_tank']:<10.3f} {test_case['final_tank']:<10.3f} "
                  f"{test_case['total_refueled']:<10.3f} {'FAILED':<10} {error_msg}")
    
    print("\nAnalýza výsledků:")
    print("-" * 40)
    print(f"Celkem testů: {num_tests}")
    print(f"Úspěšných testů: {successful_tests}")
    print(f"Neúspěšných testů: {failed_tests}")
    
    if deviations:
        avg_deviation = statistics.mean(deviations)
        median_deviation = statistics.median(deviations)
        max_deviation = max(deviations)
        min_deviation = min(deviations)
        
        print(f"\nStatistiky odchylek od cílové hodnoty:")
        print(f"Průměrná odchylka: {avg_deviation:.2f}%")
        print(f"Mediánová odchylka: {median_deviation:.2f}%")
        print(f"Minimální odchylka: {min_deviation:.2f}%")
        print(f"Maximální odchylka: {max_deviation:.2f}%")

if __name__ == "__main__":
    run_algorithm_tests(10)  # Run 10 tests 
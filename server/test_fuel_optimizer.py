import unittest
from datetime import datetime, timedelta
from fuel_optimizer import (
    State,
    calculate_fuel_consumption,
    validate_state,
    get_next_states,
    MAX_TANK_CAPACITY
)

class TestFuelOptimizer(unittest.TestCase):
    def setUp(self):
        self.start_date = datetime(2024, 1, 1)

    def test_validate_state(self):
        """Test state validation logic."""
        # Valid state
        valid_state = State(tank=50.0, date=self.start_date)
        self.assertTrue(validate_state(valid_state))
        # Invalid states
        negative_tank = State(tank=-1.0, date=self.start_date)
        self.assertFalse(validate_state(negative_tank))
        over_capacity = State(tank=MAX_TANK_CAPACITY + 1, date=self.start_date)
        self.assertFalse(validate_state(over_capacity))

    def test_calculate_fuel_consumption(self):
        """Test fuel consumption calculations."""
        # Test with known values
        self.assertAlmostEqual(calculate_fuel_consumption(70), 3.5)
        self.assertAlmostEqual(calculate_fuel_consumption(35), 1.75)
        self.assertAlmostEqual(calculate_fuel_consumption(105), 5.25)

    def test_get_next_states(self):
        """Test next state generation."""
        current_state = State(tank=30.0, date=self.start_date)
        next_states = get_next_states(current_state)
        # Should include refueling and possible routes
        self.assertTrue(any(s.action == "Refuel 50L" for s in next_states))
        self.assertTrue(any(s.action == "Drive 35km" for s in next_states))
        # Test state after refueling
        refuel_state = next(s for s in next_states if s.action == "Refuel 50L")
        self.assertEqual(refuel_state.tank, 80.0)
        self.assertEqual(refuel_state.date, self.start_date)
        # Test state after driving
        drive_state = next(s for s in next_states if s.action == "Drive 35km")
        self.assertAlmostEqual(drive_state.tank, 28.25)  # 30 - 1.75
        self.assertEqual(drive_state.date, self.start_date + timedelta(days=1))

if __name__ == '__main__':
    unittest.main()
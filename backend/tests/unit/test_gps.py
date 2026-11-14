from app.utils.gps import calculate_distance, is_within_radius

class TestGPS:
    def test_distance_zero(self):
        assert calculate_distance(28.0, 77.0, 28.0, 77.0) == 0.0

    def test_radius_check(self):
        within, dist = is_within_radius(28.5450, 77.1926, 28.5452, 77.1926, 100)
        assert within is True
        assert dist < 100

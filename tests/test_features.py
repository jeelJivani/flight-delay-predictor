from src.fetch import haversine_distance

def test_haversine_munich():
    # Munich Airport to Marienplatz (city centre)
    distance = haversine_distance(48.3538, 11.7861, 48.1374, 11.5755)
    assert 25 < distance < 32
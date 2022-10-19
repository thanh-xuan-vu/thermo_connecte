from test.integration.sim_sensor import SimulatedSensor

def test_sim_sensor_zero():
    sensor = SimulatedSensor()
    sensor.set_temperature(0)
    outputs = sensor.get_temperature()
    temperature = outputs['temperature']
    assert temperature == 0, 'Must be 0'

def test_sim_sensor_None():
    sensor = SimulatedSensor()
    sensor.set_temperature(None)
    outputs = sensor.get_temperature()
    temperature = outputs['temperature']
    assert temperature is None, 'Must be None'
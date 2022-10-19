import pytest
from datetime import timedelta

from src import main, google_notifier
# from src.main import ThermoConnecte
from src.google_notifier import GoogleNotifier
from test.integration.sim_sensor import SimulatedSensor
from test.integration.sim_thermo import SimThermoConnecte

@pytest.fixture
def sim_thermo() : 
    sensor = SimulatedSensor()
    notifier = GoogleNotifier(config_path='test/integration/config/config_google.json')
    thermo = SimThermoConnecte(sensor=sensor, notifier=notifier, 
                config_path='test/integration/config/config.json')
    thermo._notif_delay = 10
    return thermo 


def test_run_ok(sim_thermo) : 
    temperatures = [-10.1]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok']['status'] is True and \
                            last_state['ok']['notif_sent'] is False and \
                            last_state['high_temp'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state
                            

def test_run_ok_2_disconnection(sim_thermo) : 
    temperatures = [-11, None]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok'] == sim_thermo._none_state and \
                            last_state['high_temp'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected']['status'] is True and \
                            last_state['sensor_not_connected']['notif_sent'] is True 
       

def test_run_ok_2_hightemp_1st_time(sim_thermo):
    temperatures = [-11, -10]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state and \
                            last_state['high_temp']['status'] is True
                            # last_state['sensor_not_connected']['notif_sent'] is True 
        

def test_run_ok_2_hightemp_short_period(sim_thermo):
    temperatures = [-11, -10, -10]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state and \
                            last_state['high_temp']['status'] is True
                            # last_state['sensor_not_connected']['notif_sent'] is True 
       

def test_run_ok_2_hightemp_alert(sim_thermo):
    temperatures = [-11, -10, -10, -9, -8,-6, -5, -5, -7, 1, 2,3.]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state and \
                            last_state['high_temp']['status'] is True and \
                            last_state['high_temp']['notif_sent'] is True 
     
def test_disconnection_2_ok(sim_thermo) : 
    temperatures = [None, -11]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok']['status'] is True and \
                            last_state['ok']['notif_sent'] is True and \
                            last_state['high_temp'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state
                

def test_hightemp_2_ok(sim_thermo) : 
    temperatures = [-11, -10, -10, -9, -8,-6, -5, -5, -7, 1, 2,3., -11]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok']['status'] is True and \
                            last_state['ok']['notif_sent'] is True and \
                            last_state['high_temp'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state
                
def test_run_hightemp_short_period_2_ok(sim_thermo): 
    temperatures = [-11, -10, -10, -11]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok']['status'] is True and \
                            last_state['ok']['notif_sent'] is False and \
                            last_state['high_temp'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state

def test_run_hightemp_short_period_disconnection_2_ok(sim_thermo): 
    temperatures = [-11, -10, None, -11]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok']['status'] is True and \
                            last_state['ok']['notif_sent'] is True and \
                            last_state['high_temp'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state

def test_disconnection_hightemp_2_ok(sim_thermo) : 
    temperatures = [-11, -10, None, -9, -8,None, -5, -5, -7, 1, 2,3., -11]
    sim_thermo.run(temperatures)
    last_state = sim_thermo._last_state
    assert last_state['ok']['status'] is True and \
                            last_state['ok']['notif_sent'] is True and \
                            last_state['high_temp'] == sim_thermo._none_state and \
                            last_state['sensor_not_connected'] == sim_thermo._none_state
                



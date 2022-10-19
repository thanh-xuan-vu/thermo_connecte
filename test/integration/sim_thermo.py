from time import sleep

# from test.integration.sim_sensor import SimulatedSensor
# from src.notifier import Notifier
from src.main import ThermoConnecte

class SimThermoConnecte(ThermoConnecte) : 
    def run(self, temperatures:list=[]) : 
        for temperature in temperatures : 
            self._sensor.set_temperature(temperature)
            self._update()
            sleep(1)
    
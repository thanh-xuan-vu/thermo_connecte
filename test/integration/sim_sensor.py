import logging 
from datetime import datetime
from src.sensor import Sensor

logger = logging.getLogger(__name__)

class SimulatedSensor(Sensor) : 
    def __init__(self) -> None:
        self._temperature = None 
        
    def set_temperature(self, temperature=None) : 
        self._temperature = temperature

    def get_temperature(self):
        return {'time':datetime.now(), 'temperature':self._temperature}

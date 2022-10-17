from enum import Enum, auto 

class AlertLevel(Enum) :
    LOW = auto()
    HIGH = auto()

class Notifier() : 
    def notify_alert(self, alert_level: AlertLevel, message) : 
        raise NotImplementedError("Notifier is an abstract class. Redefine this function in the inherited class instead.")

    def log(self, frigo_name, sensor_id, temp, temp_max, date, time, status) : 
        raise NotImplementedError("Notifier is an abstract class. Redefine this function in the inherited class instead.")

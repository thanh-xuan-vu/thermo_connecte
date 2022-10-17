from datetime import timedelta
# import random 
from time import sleep

from src.parse_opts import parse_opts 
from src.sensor import Sensor
from src.bme_sensor import BME280
from src.notifier import AlertLevel, Notifier
from src.google_notifier import GoogleNotifier

import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(
    # filename='run.log', filemode='a', 
    handlers=[RotatingFileHandler('./run.log', maxBytes=1000000, backupCount=5)], # 5 log files max 1Mb
    level=logging.INFO, format='%(asctime)s:  %(levelname)s  :%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class ThermoConnecte() : 
    _none_state = {'status': False, 'notif_sent': False, 'first_time': None}

    def __init__(self, sensor:Sensor=Sensor(), 
                        notifier:Notifier=Notifier(), 
                        config_path='config/config.json') : 
        # parse parameters
        try : 
            opts = parse_opts(config_path)
            self._frigo_name = opts.get('frigo_name', None)
            self._sensor_id = opts.get('sensor_id', None)
            self._max_temperature = opts.get('max_temperature', None)
            self._pause_time = opts.get('pause_time', 600)
            self._notif_delay = opts.get('delay', self._pause_time * 2) # in second
        except Exception as e : 
            logger.error('Failed to parse connected thermometer config')
            raise e
        self._last_state = {'ok': self._none_state,
                            'high_temp': self._none_state,
                            'sensor_not_connected': self._none_state,
                            }
        self._status_long_name = {'ok': 'OK', 
                            'high_temp': 'Température élevée',
                            'sensor_not_connected': 'Pas de connexion au capteur',
                            }
        self._current_status = 'ok'
        self.set_sensor(sensor)
        self.set_notifier(notifier) 
    
    def set_sensor(self, sensor: Sensor) : 
        self._sensor = sensor

    def set_notifier(self, notifier: Notifier) :  
        self._notifier = notifier 
    
    def _update(self) : 
        outputs = self._sensor.get_temperature() 
        temperature = outputs['temperature']
        timestamp = outputs['time']
        timestamp_date = timestamp.strftime("%Y-%m-%d")
        timestamp_time = timestamp.strftime("%H:%M:%S")

        logger.info(f'Current temperature {temperature}')

        # update current status wrt current temperature 
        if temperature is None : 
            current_status = 'sensor_not_connected'
        elif temperature >= self._max_temperature : 
            current_status = 'high_temp'
        else : 
            current_status = 'ok'
        self._current_status = current_status
        logger.info(f'Status : {self._status_long_name[current_status]}')
        # update last state and message if needed 
        message = None 
        alert_level = AlertLevel.LOW

        if self._last_state[current_status]['status'] is False : # first time status changes
            self._last_state[current_status] = {'status': True, 'notif_sent': False, 'first_time': timestamp}
            is_status_changed = True 
        else : 
            is_status_changed = False 

        if current_status == 'ok' : 
            if is_status_changed : # first time status returns to ok
                message = f'Statut Frigo {self._frigo_name} : OK, \t {timestamp_date}, {timestamp_time}.'
                # update last state
                self._last_state['high_temp'] = self._none_state
                self._last_state['sensor_not_connected'] = self._none_state
        
        elif current_status == 'high_temp' : 
            if is_status_changed : 
                self._last_state['ok'] = self._none_state
            duration = timestamp - self._last_state['high_temp']['first_time']
            if self._last_state['high_temp']['notif_sent'] is False and \
                    duration >= timedelta(seconds=self._notif_delay) : 
                message = f'ALERTE FRIGO {self._frigo_name} : température trop élevée depuis plus de {int(duration.total_seconds()/60)} minutes, actuelle à {temperature}°C, limite à {self._max_temperature}°C, \t {timestamp_date}, {timestamp_time}.'
                alert_level = AlertLevel.HIGH

        elif current_status == 'sensor_not_connected' : 
            if is_status_changed : # first time status changes
                self._last_state['ok'] = self._none_state
                message = f'ALERTE FRIGO {self._frigo_name} : pas de connexion entre le capteur et le Raspberry pi.'
        # send message 
        if message is not None :
            try : 
                self._notifier.notify_alert(alert_level, message)
                self._last_state[current_status]['notif_sent'] = True 
                logger.info(f'Message is sent to chat group : {message}')
            except Exception as e : 
                logger.error(e)
                logger.error('Error while sending message to chat group')
            
        try : 
            # update google sheet 
            self._notifier.log(self._frigo_name, self._sensor_id, temperature, self._max_temperature, 
                    timestamp_date, timestamp_time, self._status_long_name[current_status])
            logger.info('Google sheet is updated')
        except Exception as e : 
            logger.error(e)
            logger.error('Error while updating google sheet')
        
        self._temperature = temperature
        self._timestamp = timestamp
            
    def run(self):
        while True :
            # get periodical sensor information
            self._update()
            sleep(self._pause_time)


if __name__ == '__main__' :
    # main()
    try : 
        sensor = BME280()
        notifier = GoogleNotifier()
        thermo = ThermoConnecte(sensor=sensor, notifier=notifier)

        thermo.run()
    except Exception as e : 
        logger.error(e)
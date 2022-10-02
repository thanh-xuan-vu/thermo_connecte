from datetime import datetime, timedelta
import random 
from time import sleep
from src import get_temperature
# from src.send_email import create_email
# from src.send_email import send_secure_gmail
from src.send_chat import create_message, send_chat
from src.update_sheet import update_sheet, parse_opts

import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(
# filename='run.log', filemode='a', 
handlers=[RotatingFileHandler('./run.log', maxBytes=1000000, backupCount=5)], # 5 log files max 1Mb
level=logging.INFO, format='%(asctime)s:  %(levelname)s  :%(name)s: %(message)s')
logger = logging.getLogger(__name__)


class ThermoConnecte() : 

    def __init__(self) : 
        # parse parameters
        opts = parse_opts()
        self.frigo_name = opts.get('frigo_name', None)
        self.sensor_id = opts.get('sensor_id', None)
        self.address = opts.get('address', None)

        self.max_temperature = opts.get('max_temperature', None)
        self.pause_time = opts.get('pause_time', None)
        self.thermo_status = 0   # default status 
        self.delay = opts.get('delay', self.pause_time * 2) # in second

        self.webhook = opts.get('groupe_chat_webhook', None)
        self.scopes = opts.get('scopes', None)



# def main_email() :

#     opts = parse_opts()      
    # sensor_name = opts.get('sensor_name', None)
    # address = opts.get('address', None)
    # max_temperature = opts.get('max_temperature', None)
    # pause_time = opts.get('pause_time', None)
#     # get periodical sensor information 
#     config = get_temperature.get_config(address)
#     while True :
#         outputs = get_temperature.read_bme280(**config)
#         temperature = outputs['temperature']
#         if temperature >= max_temperature :
#             time = outputs['time']
#             logger.warning(f'{time} : Current temperature ({temperature}°C) is higher than normal ({max_temperature}°C).')

#             # Send email
#             sender_email = 'thermometre.connecte@lacoopsurmer.fr'
#             receiver_email = 'thermometre.connecte@lacoopsurmer.fr' 
#             # TODO: change sender and receiver
#             message = create_email(sender_email, 
#                         receiver_email, 
#                         sensor_name=sensor_name, 
#                         sensor_data={'temperature': temperature, 'time': time},
#                         max_temperature=max_temperature)
#             send_secure_gmail(message)
#             logger.info(f'De {sender_email}')
#             logger.info(f'A {receiver_email}')
#         sleep(pause_time)

def main() :
    # parse parameters
    opts = parse_opts()
    frigo_name = opts.get('frigo_name', None)
    sensor_id = opts.get('sensor_id', None)
    address = opts.get('address', None)
    max_temperature = opts.get('max_temperature', None)
    pause_time = opts.get('pause_time', 600)
    webhook = opts.get('test_webhook', None)
    scopes = opts.get('scopes', None)

    thermo_status=0   # default status 
    alerte_sent, alerte_connect_sent = False, False
    tem_trigger, conn_trigger = False, False 
    delay = opts.get('delay', pause_time * 2) # in second

    # check config file
    if None in [frigo_name, sensor_id, address, max_temperature, pause_time, webhook, scopes] : 
        logger.error('Config file not found at token/config.json.')
        return
    
      # get pi config
    try : 
        pi_config = get_temperature.get_config(int(address, 16)) 
    except Exception as e : 
        pi_config = None 
        logger.error(e)
        logger.warning('Failed to get Pi configuration')
        # return 

    # get periodical sensor information
    while True :
        try : 
            outputs = get_temperature.read_bme280(**pi_config)             
        except Exception as e :
            logger.error('Cannot connect to sensor')
            logger.error(e)
            # outputs = {'time':datetime.now(), 'temperature':None}
            outputs = {'time':datetime.now(), 'temperature':random.choice([None, -12, -9, -9, -9,])}
        
        temperature = outputs['temperature']
        time = outputs['time']
        logger.info(f'Current temperature {temperature}')

        # temperature normal, update google sheet
        if temperature is not None : 
            if temperature < max_temperature  :  # thermo_status == 0
                logger.info(f'Status : OK (<{max_temperature}°C)') # log status 
                if tem_trigger or conn_trigger : 
                    # send ok message 
                    message = {'text': 
                                f'*Statut Frigo {frigo_name}* : OK, \t {time.strftime("%Y-%m-%d")} {time.strftime("%H:%M:%S")}.'}
                    _ = send_chat(message, webhook)
                    alerte_connect_sent, alerte_sent = False, False 
                    tem_trigger, conn_trigger = False, False 

                thermo_status = 0 
                # value to send to google sheet
                value=[[frigo_name, str(temperature), str(max_temperature),
                                    time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'OK']]

            # temperature too high, send a chat message, update google sheet
            elif temperature >= max_temperature :  # thermo_status == 1
                if thermo_status != 1 : # status change
                    start_time = time # datetime instance
                    # alerte_sent = False 
                thermo_status = 1 

                if time - start_time < timedelta(seconds=delay) : 
                    tem_trigger = False 
                    logger.warning(f'Status : Temperature too high (>={max_temperature}°C)')
                else : 
                    tem_trigger = True 
                    logger.warning(f'Status : Temperature too high (>={max_temperature}°C) for a long period {round(delay/60)} minutes.')
                    if not alerte_sent : 
                        message = create_message(sensor_name=frigo_name,
                                    sensor_data={'temperature': temperature, 'time': time.strftime("%Y-%m-%d %H:%M:%S")},
                                    max_temperature=max_temperature)
                        alerte_sent = send_chat(message, webhook) # send chat until success

                # value to send to google sheet
                value=[[frigo_name, str(temperature), str(max_temperature), 
                                            time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'Température élevée']]

        # sensor not connected, update google sheet
        elif temperature is None : # thermo_status == -1
            logger.warning('Status : No connection to sensor')
            conn_trigger = True 
            if thermo_status != 2 or not alerte_connect_sent : # status change
                # send chat message
                message = {'text': f'*Alerte Frigo {frigo_name}* : pas de connexion entre le capteur et le Raspberry pi.'}
                alerte_connect_sent = send_chat(message, webhook)
                
            value=[[frigo_name, str(temperature), str(max_temperature), 
                                        time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'Pas de connexion au capteur']]
            thermo_status = 2
        
        # send info to google sheet
        update_sheet(value=value, opts=opts, creds=None) 

        sleep(pause_time)

if __name__ == '__main__' :
    main()

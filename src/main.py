from datetime import datetime
import json
from time import sleep
from src import get_temperature
# from src.send_email import create_email
# from src.send_email import send_secure_gmail
from src.send_chat import create_message, send_chat
from src.update_sheet import update_sheet

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:  %(levelname)s  :%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# def main_email() :

#     sensor_name, address, max_temperature, pause_time, _ = parse_opts()
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
#             # TODO: send data to server 

def main() :
    sensor_name, address, max_temperature, pause_time, url,_ = parse_opts()

    # check config file
    if None in [sensor_name, address, max_temperature, pause_time, url] : 
        logger.error('Config file not found at token/config.json.')
        return
    # get pi config
    try : 
        pi_config = get_temperature.get_config(address) 
    except : pi_config = None 

    # get periodical sensor information 
    while True :
        if pi_config :
            outputs = get_temperature.read_bme280(**pi_config) 
        else :
            logger.error('Cannot connect to sensor')
            outputs = {'time':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'temperature':None}
        
        temperature = outputs['temperature']
        time = outputs['time']

        # temperature normal, update google sheet
        if temperature < max_temperature and temperature is not None :
            update_sheet(idx=sensor_name, value=[[sensor_name, str(temperature), str(max_temperature), time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'OK']]) 

        # temperature too high, send a chat message, update google sheet
        elif temperature >= max_temperature and temperature is not None :
            logger.warning(f'{time} : Current temperature ({temperature}°C) is higher than normal ({max_temperature}°C).')
            message = create_message(sensor_name=sensor_name,
                        sensor_data={'temperature': temperature, 'time': time},
                        max_temperature=max_temperature)
            send_chat(message, url)
            logger.info('Message sent to group chat.')
            # send info to google sheet
            update_sheet(idx=sensor_name, value=[[sensor_name, str(temperature), str(max_temperature), time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'Température élevée']]) 

        # sensor not connected, update google sheet
        elif temperature is None :
            # send chat message
            logger.warning(f'{time} : No signal from sensor.')
            message = {'text': f'<users/all> *Frigo {sensor_name}* : pas de connexion entre le capteur et le Raspberry pi.'}
            logger.info('Message sent to group chat.')
            # send info to google sheet
            update_sheet(idx=sensor_name, value=[[sensor_name, str(temperature), str(max_temperature), time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'Pas de connexion au capteur']]) 

        sleep(pause_time)

def parse_opts(fp='token/config.json'):
    # parse config 
    try : 
        with open(fp, 'r') as fn :
            opts = json.load(fn)
            logger.info(opts)
        sensor_name = opts.get('sensor_name', None)
        address = opts.get('address', None)
        max_temperature = opts.get('max_temperature', None)
        pause_time = opts.get('pause_time', None)
        url = opts.get('groupe_chat_webhook', None)
    except FileExistsError as e :
        logger.error(e)
    return sensor_name,address,max_temperature,pause_time,url

if __name__ == '__main__' :
    main()
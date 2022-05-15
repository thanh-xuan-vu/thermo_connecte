from datetime import datetime
import json
from time import sleep
from src import get_temperature
# from src.send_email import create_email
# from src.send_email import send_secure_gmail
from src.send_chat import create_message, send_chat
from src.update_sheet import update_sheet
from src.update_sheet import parse_opts

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:  %(levelname)s  :%(name)s: %(message)s')
logger = logging.getLogger(__name__)


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
    sensor_name = opts.get('sensor_name', None)
    address = opts.get('address', None)
    max_temperature = opts.get('max_temperature', None)
    pause_time = opts.get('pause_time', None)
    webhook = opts.get('groupe_chat_webhook', None)

    # check config file
    if None in [sensor_name, address, max_temperature, pause_time, webhook] : 
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
            outputs = {'time':datetime.now(), 'temperature':None}
        
        temperature = outputs['temperature']
        time = outputs['time']

        # temperature normal, update google sheet
        if temperature is not None : 
            if temperature < max_temperature  :
                # value to send to google sheet
                value=[[sensor_name, str(temperature), str(max_temperature),
                                    time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'OK']]

            # temperature too high, send a chat message, update google sheet
            elif temperature >= max_temperature :
                logger.warning(f'{time} : Current temperature ({temperature}°C) is higher than normal ({max_temperature}°C).')
                message = create_message(sensor_name=sensor_name,
                            sensor_data={'temperature': temperature, 'time': time},
                            max_temperature=max_temperature)
                send_chat(message, webhook)
                logger.info('Message sent to group chat.')
                logger.info(message)
                # value to send to google sheet
                value=[[sensor_name, str(temperature), str(max_temperature), 
                                            time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'Température élevée']]

        # sensor not connected, update google sheet
        elif temperature is None :
            # send chat message
            message = {'text': f'<users/all> *Frigo {sensor_name}* : pas de connexion entre le capteur et le Raspberry pi.'}
            send_chat(message, webhook)
            logger.info('Message sent to group chat.')
            logger.info(message)
            value=[[sensor_name, str(temperature), str(max_temperature), 
                                        time.strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"), 'Pas de connexion au capteur']]
        # send info to google sheet
        update_sheet(value=value, opts=opts) 
        sleep(pause_time)

if __name__ == '__main__' :
    main()
#!/bin/python

import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os 
from email.mime.text import MIMEText

import logging
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']



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
#             sender_email = ''
#             receiver_email = '' 
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

def send_secure_gmail(message):
    """Send secure email with Gmail API.    """

    creds = get_creds()

    try:
        # Call the Gmail API
        with build('gmail', 'v1', credentials=creds) as service :
            message = (service.users().messages().send(userId='me', body=message)
                   .execute())
        logger.info('Message Id: %s est envoyé' % message['id'])
        return message
    except Exception as error:
        logger.error(error)

def get_creds(scopes=SCOPES):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    token_fp = 'token/token.json'
    if os.path.exists(token_fp):
        creds = Credentials.from_authorized_user_file(token_fp, scopes)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'token/credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_fp, 'w') as token:
            token.write(creds.to_json())
    return creds

    # TODO: add guide to forward port in first time authentication 
    # ssh -N -L localhost:port_number:localhost:port_number raspberrypi_ip

def create_email(sender_email, receiver_email, sensor_name='', 
        sensor_data=None, max_temperature=None) :

    # Extract sensor's data
    temperature = sensor_data['temperature']
    time = sensor_data['time']

    # Build message
    text = f'''\
Bonjour,

Je suis le thermomètre connecté du Frigogidaire. Actuellement, je constate une température plus élevée que normalement comme ci-dessous  
    
    - Nom : {sensor_name}
    - Température actuelle : {temperature}°C (Alerte à {max_temperature}°C)
    - Heure : {time}

Merci d'inspecter ce Frigogidaire et réagir au plus vite !  

Bien cordialement, 
Raspberry Pi Zero du Group informatique
La coop sur mer 
\n\n\n
N/B : ceci est un message automatique, merci de ne pas répondre directement. Vous pouvez signaler au informatique@lacoopsurmer.fr. 
    '''

    message = MIMEText(text)
    message['Subject'] = f'WARNING : Température du {sensor_name} trop élevée'
    message['From'] = sender_email
    message['To'] = receiver_email
    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
    
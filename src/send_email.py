#!/bin/python

import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os 
from time import sleep
import datetime
from getpass import getpass
import smtplib, ssl
from email.message import EmailMessage
from email.mime.text import MIMEText

from src import get_temperature

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']


def send_secure_gmail(message):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_fp = 'token/token.json'
    if os.path.exists(token_fp):
        creds = Credentials.from_authorized_user_file(token_fp, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'token/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_fp, 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        with build('gmail', 'v1', credentials=creds) as service :
            message = (service.users().messages().send(userId='me', body=message)
                   .execute())
        logger.info('Message Id: %s est envoyé' % message['id'])
        return message
    except Exception as error:
        logger.error(error)



def create_message(sender_email, receiver_email, sensor_name='', 
        sensor_data=None, max_temperature=None) :
    # TODO: group data from multiple sensors in a single email

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

def main() :

    # TODO: get periodical sensor information 
    # config = get_temperature.get_config()
    # while True :
    #     outputs = get_temperature.read_bme280(config)
    #     if outputs['temperature'] >= max_temperature :
    #         logger.warning(f'{outputs[0]} : Current temperature ({outputs[1]}°C) is higher than normal ({max_temperature}°C).')
    #         send_less_secure_mail()
    #     sleep(pause_time)

    temperature = 20
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_name = 'Raspberry Pi Test'

    # Send email
    sender_email = 'thermometre.connecte@lacoopsurmer.fr'
    receiver_email = 'thermometre.connecte@lacoopsurmer.fr' 
    # TODO: change sender and receiver
    message = create_message(sender_email, receiver_email, sensor_name=sensor_name, 
                sensor_data={'temperature': temperature, 'time': time},
                max_temperature=10)

    send_secure_gmail(message)

if __name__ == '__main__' :
    main()

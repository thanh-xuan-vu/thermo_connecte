#!/bin/python

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

from time import sleep
from getpass import getpass
import smtplib, ssl
from email.message import EmailMessage

from src import get_temperature

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


# def send_gmail():
#     """Shows basic usage of the Gmail API.
#     Lists the user's Gmail labels.
#     """
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     try:
#         # Call the Gmail API
#         service = build('gmail', 'v1', credentials=creds)
#         results = service.users().labels().list(userId='me').execute()
#         labels = results.get('labels', [])

#         if not labels:
#             print('No labels found.')
#             return
#         print('Labels:')
#         for label in labels:
#             print(label['name'])

#     except HttpError as error:
#         # TODO(developer) - Handle errors from gmail API.
#         print(f'An error occurred: {error}')



def create_message(sender_email, receiver_email, sensor_name='', 
        sensor_data=None, max_temperature=None) :
    # TODO: group data from multiple sensors in a single email

    # Extract sensor's data
    temperature = sensor_data['temperature']
    time = sensor_data['time']
    # Build message
    message = EmailMessage()
    message['Subject'] = f'WARNING : Température du {sensor_name} trop élevée'
    message['From'] = sender_email
    message['To'] = receiver_email
    text = f'''\
    Bonjour,

    Je suis le thermomètre connecté du Frigogidaire. Actuellement, 
    je constate une température plus élevée que normalement à  

    \t {sensor_name} \t à \t {time}.  

    C'est à dire {temperature}°C au lieu de {max_temperature}°C.
    Merci d'inspecter ce Frigogidaire et réagir au plus vite ! 

    Bien cordialement, 
    Raspberry Pi Zero du Group informatique
    La coop sur mer 
    '''
    message.set_content(text)
    return message

def send_less_secure_mail(sensor_name='', sensor_data=None,
                max_temperature=None):
    port = 465  # For 
    host = "smtp.gmail.com"
    # port = 1025
    # host = "localhost"

    # Create a secure SSL context
    context = ssl.create_default_context()
    sender_email = 'thermometre.connecte@lacoopsurmer.fr'
    receiver_email = 'thermometre.connecte@lacoopsurmer.fr'
    password = getpass(f"\nEmail to: {receiver_email}. \nType your password and press enter: \n")

    with smtplib.SMTP_SSL(host, port, context=context) as server:
    # with smtplib.SMTP(host, port) as server:
        # Send email here
        message = create_message(sender_email, receiver_email, sensor_name, 
                                sensor_data, max_temperature)
        server.login(sender_email, password)
        res = server.send_message(message)
        if not res : 
            logger.info('Email envoyé.')
        else : 
            logger.info('Erreur : pas de mél envoyé')

def main(max_temperature=None, pause_time=2) :

    config = get_temperature.get_config()
    while True :
        outputs = get_temperature.read_bme280(config)
        if outputs['temperature'] >= max_temperature :
            logger.warning(f'{outputs[0]} : Current temperature ({outputs[1]}°C) is higher than normal ({max_temperature}°C).')
            send_less_secure_mail()
        sleep(pause_time)


if __name__ == '__main__' :
    # main()
    send_less_secure_mail(sensor_name='Raspberry Pi Test', 
                sensor_data={'temperature':20, 'time':'17:50 11-04-2022'},
                max_temperature=10)
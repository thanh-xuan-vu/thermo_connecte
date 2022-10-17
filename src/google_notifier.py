
from datetime import datetime
import os
from httplib2 import Http
from json import dumps
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import logging
from .notifier import AlertLevel, Notifier 
from .parse_opts import parse_opts 
logger = logging.getLogger(__name__)


class GoogleNotifier(Notifier) : 

    def __init__(self, config_path='config/config_google.json') : 
        super().__init__()
        try : 
            opts = parse_opts(config_path)
            self._url = opts['groupe_chat_webhook']
            self._scopes = opts['scopes']
            self._spreadsheet_id = opts['spreadsheet_id']
            self._creds = self.__get_creds(self._scopes)
        except Exception as e : 
            logger.error("Failed to parse Google API related config.")
            raise e 

    def __format_msg(self, message: str, alert_level: AlertLevel) :
        if alert_level == AlertLevel.HIGH : 
            return {'text': '<users/all> ' + message} 
        elif alert_level == AlertLevel.LOW : 
            return {'text': message}


    def notify_alert(self, alert_level: AlertLevel, message): 
        # (bot_message, url) :
        """Hangouts Chat incoming webhook quickstart."""
        bot_message = self.__format_msg(message, alert_level)
        message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

        http_obj = Http()
        try :
            response = http_obj.request(
                uri=self._url,
                method='POST',
                headers=message_headers,
                body=dumps(bot_message),
            )
            if response[0].status == 200 :
                logger.info('Message sent to group chat.')
                logger.info(f'Message content: {bot_message}')
                return True
            else : 
                logger.error('Failed to send message to group chat')
                return False
            
        except Exception as e : 
            logger.error(f'{type(e)} {e}')
            return False 

    @staticmethod
    def __get_creds(scopes, token_dir='config', token_fn='token.json') :
         
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_fp = os.path.join(token_dir, token_fn)
        if os.path.exists(token_fp):
            creds = Credentials.from_authorized_user_file(token_fp, scopes)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(token_dir, 'credentials.json'), scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_fp, 'w') as token:
                token.write(creds.to_json())
        return creds

    def __write_sheet_row(self, value, sheet, sheet_name, cols_range='A2:F2', spreadsheet_id=None):
        body = {
                'valueInputOption': "RAW",
                'data': [
                {
                    'range': f'{sheet_name}!{cols_range}',
                    'values': value # [[nom_frigo, temperature, alerte, jour, heure, etat]]
                },
            ]}
        response = sheet.values().batchUpdate(spreadsheetId=spreadsheet_id,
                                        body=body,
                                        ).execute()

        return response


    def __format_log_row(self, frigo_name, temp, temp_max, date, time, status) : 
        value=[[frigo_name, temp, temp_max, date, time, status]]
        return value 

    def log(self, frigo_name, sensor_id, temp, temp_max, date, time, status) :
        spreadsheet_id = self._spreadsheet_id
        sheet_title = str(frigo_name)
        try:
            service = build('sheets', 'v4', credentials=self._creds)

            # Call the Sheets API
            sheet = service.spreadsheets()

            # Update General sheet
            value = self.__format_log_row(frigo_name, temp, temp_max, date, time, status)
            _ = self.__write_sheet_row(value, sheet, 'Général', 
                                    cols_range=f'A{int(sensor_id)+1}:F{int(sensor_id)+1}', 
                                    spreadsheet_id=spreadsheet_id)
            logger.info(f'Updated temperature in sheet General')

            # Create frigo_id sheet if needed
            sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            sheet_title_list = [sh['properties']['title'] for sh in sheets]
            
            if  sheet_title not in sheet_title_list : 
                _ = self.__create_named_sheet(spreadsheet_id, sheet_title, sheet)
                # Write title row
                title = self.__format_log_row('Nom du frigogidaire', 'Température', 'Alerte', 'Date', 'Heure', 'Etat')
                _ = self.__write_sheet_row(value=title, sheet=sheet, sheet_name=sheet_title, 
                                        cols_range='A1:F1', spreadsheet_id=spreadsheet_id)
                logger.info(f'Create sheet {sheet_title}')

                sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
                sheets = sheet_metadata.get('sheets', '')
            
            # update log in frigo_id sheet
            sheetId_list = [sh['properties']['sheetId'] for sh in sheets if sh['properties']['title']==sheet_title]
            sheet_id = sheetId_list[0]
            _ = self.__delete_n_insert_row(spreadsheet_id, sheet, sheet_id)
            _ = self.__write_sheet_row(value= value, sheet=sheet, sheet_name=sheet_title, 
                                    cols_range='A2:F2', spreadsheet_id=spreadsheet_id) # write in row 2
            logger.info(f' Updated temperature to sheet {sheet_title}')
            # logger.info(' nom_frigo, temperature, alerte, jour, heure, etat : ')
            # logger.info(value)
        except Exception as err:
            logger.error(f'{type(err)} {err}')
            logger.warning(f' Failed to update temperature to Google sheet')
            raise err 

    def __delete_n_insert_row(self, spreadsheet_id, sheet, sheet_id, insert_row=1, del_row=900):
        body = { "requests": [
                {
                "deleteDimension": { # delete row 900
                    "range": {
                    "sheetId": sheet_id         ,
                    "dimension": "ROWS",
                    "startIndex": del_row,
                    "endIndex": del_row+1
                    },
                    }
                },
                {
                "insertDimension": { # insert row 2
                    "range": {
                    "sheetId": sheet_id                ,
                    "dimension": "ROWS",
                    "startIndex": insert_row,
                    "endIndex": insert_row+1
                    },
                    "inheritFromBefore": True
                    }
                }
            ]
            }
        response = sheet.batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=body).execute()
        return response

    def __create_named_sheet(self, spreadsheet_id, sheet_title, sheet):
        body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': sheet_title,
                            }
                        }
                    }]
                                        }

        response = sheet.batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body=body).execute()
        return response


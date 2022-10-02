from src.send_email import get_creds

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import logging 
# logging.basicConfig(filename='run.log', filemode='a', level=logging.INFO, format='%(asctime)s:  %(levelname)s  :%(name)s: %(message)s')
logger = logging.getLogger(__name__)


# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# spreadsheet_id = "1z9GsrI7ARmHv7rM6CXzICWbeAwHZpzUeSbuoZiGZn1k"

def parse_opts(fp='token/config.json'):
    # parse config 
    try : 
        with open(fp, 'r') as fn :
            opts = json.load(fn)
            logger.info(opts)
            return opts
    except FileExistsError as e :
        logger.error(e)

def update_sheet(value=[['Test','10', '15', 'today', 'now', 'OK']], opts=None, creds=None) :
    if not opts : opts = parse_opts()
    scopes = opts.get('scopes', None)
    spreadsheet_id = opts.get('spreadsheet_id', None)
    frigo_name = opts.get('frigo_name', None)
    sensor_id = opts.get('sensor_id', None)
    sheet_title = str(frigo_name)

    if None in [scopes, spreadsheet_id, frigo_name, sensor_id] :
        logger.warning(f'Lack scopes (={scopes}) or spreadsheet_id (={spreadsheet_id}) \n \
                        or frigo_name (={frigo_name}) or sensor_id (={sensor_id}) in config file. \n \
                        Google sheet is not updated.')
        return

    if creds is None : 
        try : 
            creds = get_creds(scopes=scopes)
        except Exception as e : 
            logger.error(e)
            logger.error(f'Error while getting Google Authentification credential')
            return 
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        # TODO: create sheet General if needed
        # Update General sheet
        _ = write_sheet_row(value, sheet, 'Général', 
                                range=f'A{int(sensor_id)+1}:F{int(sensor_id)+1}', 
                                spreadsheet_id=spreadsheet_id)

        logger.info(f'Updated temperature in sheet General')

        sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_title_list = [sh['properties']['title'] for sh in sheets]
        
        # Create frigo_id sheet if needed
        if  sheet_title not in sheet_title_list : 
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_title,
                        }
                    }
                }]
                                    }

            _ = sheet.batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body).execute()
            # Write title row
            _ = write_sheet_row(value= [['Nom du frigogidaire', 'Température', 'Alerte', 'Date', 'Heure', 'Etat']], 
                            sheet=sheet, sheet_name=sheet_title, range='A1:F1', spreadsheet_id=spreadsheet_id)
            logger.info(f'Create sheet {sheet_title}')

            # update log in frigo_id sheet
            sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
        
        sheetId_list = [sh['properties']['sheetId'] for sh in sheets if sh['properties']['title']==sheet_title]
        sheet_id = sheetId_list[0]
        body = { "requests": [
            {
            "deleteDimension": { # delete row 900
                "range": {
                "sheetId": sheet_id         ,
                "dimension": "ROWS",
                "startIndex": 900,
                "endIndex": 901
                },
                }
            },
            {
            "insertDimension": { # insert row 2
                "range": {
                "sheetId": sheet_id                ,
                "dimension": "ROWS",
                "startIndex": 1,
                "endIndex": 2
                },
                "inheritFromBefore": True
                }
            }
            
        ]
        }
        _ = sheet.batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=body).execute()
        _ = write_sheet_row(value= value,  
                            sheet=sheet, sheet_name=sheet_title, range='A2:F2', spreadsheet_id=spreadsheet_id) # write in row 2
        logger.info(f' Updated temperature to sheet {sheet_title}')
        # logger.info(' nom_frigo, temperature, alerte, jour, heure, etat : ')
        # logger.info(value)
    except Exception as err:
        logger.error(f'{type(err)} {err}')
        logger.warning(f' Failed to update temperature to Google sheet')

def write_sheet_row(value, sheet, sheet_name, range='A2:F2', spreadsheet_id=None):
    body = {
            'valueInputOption': "RAW",
            'data': [
            {
                'range': f'{sheet_name}!{range}',
                'values': value # [[nom_frigo, temperature, alerte, jour, heure, etat]]
            },
        ]}
    response = sheet.values().batchUpdate(spreadsheetId=spreadsheet_id,
                                    body=body,
                                    ).execute()

    return response

if __name__ == '__main__' :
    update_sheet(value=[['Test', '10', '15', 'today', 'now', 'Température élevée']]) # current temperature, alert tempearture, date, time, status



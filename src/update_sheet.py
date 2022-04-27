from src.send_email import get_creds

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = "1z9GsrI7ARmHv7rM6CXzICWbeAwHZpzUeSbuoZiGZn1k"
FRIGO_IDX = 3
SHEET_TITLE = str(FRIGO_IDX)

def update_sheet(idx=FRIGO_IDX, value=[[SHEET_TITLE, '10', '15', 'today', 'now', 'OK']]) :
    creds = get_creds(scopes=SCOPES)
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        # Update General sheet
        response = write_sheet_row(value, sheet, 'Général', range=f'A{idx+1}:F{idx+1}')

        sheet_metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_list = [sh['properties']['title'] for sh in sheets]
        
        if  SHEET_TITLE not in sheet_list : # Create/ Update FRIGO_IDX sheet
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': SHEET_TITLE,
                        }
                    }
                }]
                                    }

            result = sheet.batchUpdate(
                    spreadsheetId=SPREADSHEET_ID,
                    body=body).execute()
            print(result)
            response = write_sheet_row(value= [['Nom du frigogidaire', 'Température', 'Alerte', 'Date', 'Heure', 'Etat']], 
                            sheet=sheet, sheet_name=SHEET_TITLE, range='A1:F1')
            print(response)    
        # update log for FRIGO_IDX
        sheet_metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheet_list = [sh['properties']['sheetId'] for sh in sheets if sh['properties']['title']==SHEET_TITLE]
        SHEET_ID = sheet_list[0]
        body = { "requests": [
            {
            "deleteDimension": { # delete row 200
                "range": {
                "sheetId": SHEET_ID         ,
                "dimension": "ROWS",
                "startIndex": 200,
                "endIndex": 201
                },
                }
            },
            {
            "insertDimension": { # insert row 2
                "range": {
                "sheetId": SHEET_ID                ,
                "dimension": "ROWS",
                "startIndex": 1,
                "endIndex": 2
                },
                "inheritFromBefore": True
                }
            }
            
        ]
        }
        result = sheet.batchUpdate(
                    spreadsheetId=SPREADSHEET_ID,
                    body=body).execute()
        print(result)
        response = write_sheet_row(value= value,  
                            sheet=sheet, sheet_name=SHEET_TITLE, range='A2:F2') # write in row 2
    except HttpError as err:
        print(err)

def write_sheet_row(value, sheet, sheet_name, range=f'A{FRIGO_IDX+1}:F{FRIGO_IDX+1}'):
    body = {
            'valueInputOption': "RAW",
            'data': [
            {
                'range': f'{sheet_name}!{range}',
                'values': value # [[nom_frigo, temperature, alerte, jour, heure, etat]]
            },
        ]}
    response = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                    body=body,
                                    ).execute()

    return response

if __name__ == '__main__' :
    update_sheet()



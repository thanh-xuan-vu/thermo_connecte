
from datetime import datetime
from httplib2 import Http
from json import dumps

import logging
logger = logging.getLogger(__name__)

def create_message(sensor_name='', 
                sensor_data=None, 
                max_temperature=None) :
    msg = f'''
    <users/all> *Alerte température trop élevée* 
    *Frigo {sensor_name}* : {sensor_data['temperature']}°C (limite à {max_temperature}°C). {sensor_data['time'].strftime("%Y-%m-%d %H:%M:%S")} 
    '''
    return {'text':msg}


def send_chat(bot_message, url) :
    """Hangouts Chat incoming webhook quickstart."""

    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

    http_obj = Http()

    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )


if __name__ == '__main__' :
    sensor_data = {'time':datetime.now(), 'temperature':20}
    url = 'https://chat.googleapis.com/v1/spaces/AAAARZvu6PE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=dZBMh0EDYOPRjg1xjmY1yY9JbkPY2P-E3edB0Z4c91c%3D'

    text_msg = create_message(sensor_name='test', 
            sensor_data=sensor_data, max_temperature=15)
    send_chat(text_msg, url)

#!/bin/python
import bme280 
import smbus2
import time
import logging

from sensor import Sensor
from parse_opts import parse_opts

logger = logging.getLogger(__name__)

class BME280(Sensor) : 
    
    def __init__(self, config_path='config/config_bme.json') : 
        super().__init__()
        try : 
            opts = self.parse_opts(config_path)
            self._config = self.get_config(opts.get('address', None))
        except Exception as e : 
            logger.error(f'Error reading config for BME280 sensor')
            raise e 

    def get_config(self, address=0x77):
        '''Get calibration config of BME280 from its address'''
        port = 1
        bus = smbus2.SMBus(port)
        time.sleep(1)
        
        calibration_params = bme280.load_calibration_params(bus, address)
        # logger.info('Configuration: ', bus, address, calibration_params)
        return {'bus':bus, 'address':address, 'calibration_params':calibration_params}

    def get_temperature(self) :
        # the sample method will take a single reading and return a
        # compensated_reading object

        bus = self._config['bus']
        address = self._config['address']
        calibration_params = self._config['calibration_params']
        data = bme280.sample(bus, address, calibration_params)

        outputs = {'time':data.timestamp, 'temperature':round(data.temperature, ndigits=1)}
        logger.info(outputs)
        return outputs

if __name__ == '__main__' :
    name = 'Raspberry Pi'
    logger.info(name)
    sensor = BME280()
    outputs = sensor.get_temperature()



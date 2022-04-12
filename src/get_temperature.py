#!/bin/python
import bme280 
import smbus2
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def get_config(address=None):
    port = 1
    if not address : 
        address = 0x77  # TODO: verify this address with i2cdetect -y 1 in terminal
    bus = smbus2.SMBus(port)
    time.sleep(1)
    
    calibration_params = bme280.load_calibration_params(bus, address)
    # logger.info('Configuration: ', bus, address, calibration_params)
    return {'bus':bus, 'address':address, 'calibration_params':calibration_params}

def read_bme280(**config) :

    # the sample method will take a single reading and return a
    # compensated_reading object
    bus = config['bus']
    address = config['address']
    calibration_params = config['calibration_params']
    data = bme280.sample(bus, address, calibration_params)
    outputs = {'time':data.timestamp, 'temperature':data.temperature}
    logger.info(outputs)
    return outputs

if __name__ == '__main__' :
    name = 'Raspberry Pi'
    logger.info(name)
    
    config = get_config()
    outputs = read_bme280(**config)



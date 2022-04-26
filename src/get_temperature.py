#!/bin/python
import bme280 
import smbus2
import time
import logging
logger = logging.getLogger(__name__)

def get_config(address=0x77):
    port = 1
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
    outputs = {'time':data.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 'temperature':round(data.temperature, ndigits=1)}
    logger.info(outputs)
    return outputs

if __name__ == '__main__' :
    name = 'Raspberry Pi'
    logger.info(name)
    
    config = get_config()
    outputs = read_bme280(**config)



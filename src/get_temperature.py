#!/bin/python
import bme280 
import smbus2

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def get_config():
    port = 1
    address = 0x76  # TODO: verify this address
    bus = smbus2.SMBus(port)

    calibration_params = bme280.load_calibration_params(bus, address)
    logger.info('Configuration: ', bus, address, calibration_params)
    return {'bus':bus, 'address':address, 'calibration_params':calibration_params}

def read_bme280(**config) :

    # the sample method will take a single reading and return a
    # compensated_reading object
    bus = config['bus']
    address = config['address']
    calibration_params = config['calibration_params']
    data = bme280.sample(bus, address, calibration_params)
    outputs = {'time':data.timestamp, 'temperature':data.temperature}
    logger.info(data)
    return outputs

if __name__ == '__main__' :
    # main()
    # send_secure_mail()
    # TODO: test with Raspberry Pi
    name = 'Raspberry Pi'
    logger.info(name)
    
    config = get_config()
    outputs = read_bme280(config)



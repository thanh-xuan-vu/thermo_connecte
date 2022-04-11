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

    return [bus, address, calibration_params]

def read_bme280(config=[]) :

    # the sample method will take a single reading and return a
    # compensated_reading object
    data = bme280.sample(*config)
    outputs = [data.timestamp, data.temperature, data.humidity, data.pressure]
    logger.info(data)
    return outputs

if __name__ == '__main__' :
    # main()
    # send_secure_mail()
    name = 'Raspberry Pi'
    logger.info(name)
    
    config = get_config()
    outputs = read_bme280(config)



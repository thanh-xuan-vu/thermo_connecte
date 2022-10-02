import json 
import logging 
logger = logging.getLogger(__name__)

def parse_opts(file_path) : 
        '''Parse parameters from file path'''
        try : 
            with open(file_path, 'r') as fn :
                opts = json.load(fn)
                logger.info(opts)
                return opts
        except FileExistsError as e :
            raise e 
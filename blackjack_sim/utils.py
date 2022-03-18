import logging
import sys

class Utils(object):

    @classmethod
    def get_logger(cls, name, log_level):

        log = logging.getLogger(name)
        log.setLevel(log_level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        log.addHandler(handler)

        return log
    

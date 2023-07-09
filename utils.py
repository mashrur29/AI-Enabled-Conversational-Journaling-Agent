from logging.handlers import TimedRotatingFileHandler
import logging


def get_logger(log_file_name, log_level='INFO'):
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)-5.5s]  %(message)s')
    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler(log_file_name, mode='a')
    file_handler.setFormatter(log_formatter)
    # rotation_handler = RotatingFileHandler (log_file_name, maxBytes=50 * 1024 * 1024, backupCount=100)
    #rotation_handler = TimedRotatingFileHandler(log_file_name, when='midnight', interval=1, backupCount=9999)
    logger.addHandler(file_handler)
    #logger.addHandler(rotation_handler)
    if log_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger


logger = get_logger(log_file_name='logs/log_', log_level='INFO')

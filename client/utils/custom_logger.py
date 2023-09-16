import logging

def setup_custom_logger(log_file_name):
    # create logger
    custom_logger = logging.getLogger("custom_logger")
    # config  logger's format and level
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
    custom_logger.setLevel(logging.DEBUG)
    # create file handler with dynamic log file name
    file_handler = logging.FileHandler('utils/' + log_file_name + '.log')
    file_handler.setFormatter(formatter)
    # add handler to logger
    custom_logger.addHandler(file_handler)
    
    return custom_logger

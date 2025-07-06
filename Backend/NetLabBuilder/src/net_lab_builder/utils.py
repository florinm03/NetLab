from ipaddress import ip_network
import logging
import re


def create_ipv4_from_subnet(subnet: str, node_count: int) -> str:
    network = ip_network(subnet, strict=False)
    base_address_int = int(network.network_address)
    new_address_int = base_address_int + node_count
    return network.network_address.__class__(new_address_int).exploded


def extract_number(name):
    # Search for a number at the end of the string
    match = re.search(r"\d+$", name)

    if match:
        return int(match.group())
    else:
        return None


class LoggerFactory(object):
    _LOG = None

    @staticmethod
    def __create_logger(log_file, log_level):
        """
        A private method that interacts with the python
        logging module
        """
        # set the logging format
        log_format = "%(asctime)s:%(levelname)s: %(message)s"

        # Initialize the class variable with logger object
        LoggerFactory._LOG = logging.getLogger(log_file)
        logging.basicConfig(
            level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S"
        )

        # set the logging level based on the user selection
        if log_level == "INFO":
            LoggerFactory._LOG.setLevel(logging.INFO)
        elif log_level == "ERROR":
            LoggerFactory._LOG.setLevel(logging.ERROR)
        elif log_level == "DEBUG":
            LoggerFactory._LOG.setLevel(logging.DEBUG)
        return LoggerFactory._LOG

    @staticmethod
    def get_logger(log_file, log_level):
        """
        A static method called by other modules to initialize logger in
        their own module
        """
        logger = LoggerFactory.__create_logger(log_file, log_level)

        # return the logger object
        return logger

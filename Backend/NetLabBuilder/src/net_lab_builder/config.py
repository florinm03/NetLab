_config = {
    "log_level": "DEBUG",  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL
    "label": "prototype",
    "router_ip_range": "0.0.1.0/24",
    "server_ip_range": "0.0.2.0/24",
    "client_ip_range": "0.0.3.0/24",
    "pcap_merge_interval": 3,
    "pcap_merge_target": "/pcap/merged.pcap",
}


def configure(**kwargs):
    """
    Updates the configuration with the given keyword arguments.
    """
    _config.update(kwargs)

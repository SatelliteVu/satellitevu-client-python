import http.client as http_client
import logging


def setup_logging(verbose=False):
    """
    Setup verbose request logging if needed
    """
    http_client.HTTPConnection.debuglevel = 1 if verbose else 0
    log_level = logging.DEBUG if verbose else logging.WARNING

    logging.basicConfig()
    logging.getLogger().setLevel(log_level)

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(log_level)
    requests_log.propagate = True

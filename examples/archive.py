import argparse
import http.client as http_client
import logging
import os
import pprint
from datetime import datetime, timedelta

from satellitevu import Client

EXAMPLES = {
    "everything": {},
    "london": {"bbox": [-1.065151, 51.163899, 0.457906, 51.802226]},
    "recent": {"sortby": [{"field": "datetime", "direction": "desc"}], "limit": 5},
    "last-month": {
        "date_from": datetime.utcnow() - timedelta(days=30),
        "date_to": datetime.utcnow(),
    },
}


def _setup_client():
    """
    Building a default client is as easy as feeding the client id and secret into the
    satellitevu.Client class
    """
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("CLIENT_ID and CLIENT_SECRET must be set")

    return Client(client_id=client_id, client_secret=client_secret)


def _setup_logging(verbose=False):
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


def archive_search(**kwargs):
    """
    Have client, will search
    """
    client = _setup_client()
    response = client.archive_v1.search(**kwargs)

    pprint.pprint(response.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--example", choices=EXAMPLES.keys(), default="everything")
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )

    args = parser.parse_args()
    _setup_logging(args.verbose)

    search_args = EXAMPLES[args.example]
    archive_search(**search_args)

import argparse
import os
import pprint
from datetime import datetime, timedelta, timezone

from common import setup_logging

from satellitevu import Client

EXAMPLES = {
    "everything": {},
    "london": {"bbox": [-1.065151, 51.163899, 0.457906, 51.802226]},
    "recent": {"sortby": [{"field": "datetime", "direction": "desc"}], "limit": 5},
    "last-month": {
        "date_from": datetime.now(tz=timezone.utc) - timedelta(days=30),
        "date_to": datetime.now(tz=timezone.utc),
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


def catalog_search(contract_id, **kwargs):
    """
    Have client, will search with a contract
    """
    client = _setup_client()
    response = client.catalog_v1.search(contract_id=contract_id, **kwargs)

    pprint.pprint(response.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("contract_id", help="A Contract ID must be provided.")
    parser.add_argument("--example", choices=EXAMPLES.keys(), default="everything")
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    search_args = EXAMPLES[args.example]
    catalog_search(contract_id=args.contract_id, **search_args)

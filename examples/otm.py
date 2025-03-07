import argparse
import os
from datetime import datetime, timedelta, timezone
from pprint import pprint
from time import sleep

from common import setup_logging

from satellitevu import Client


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


def feasibility(contract_id):
    client = _setup_client()
    now = datetime.now(tz=timezone.utc)
    response = client.otm_v2.post_feasibility(
        contract_id=contract_id,
        coordinates=[12, 52],
        date_from=now,
        date_to=now + timedelta(days=7),
        min_off_nadir=0,
        max_off_nadir=45
    )

    fid = response["id"]
    status = response["properties"]["status"]

    while status == "pending":
        sleep(2)
        print("### Polling status…", end=" ")
        response = client.otm_v2.get_feasibility(contract_id=contract_id, id=fid)
        status = response["properties"]["status"]
        print(f"{status} ###")

    print("### FINAL: ###")
    pprint(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("contract_id", help="A Contract ID must be provided.")
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    feasibility(args.contract_id)

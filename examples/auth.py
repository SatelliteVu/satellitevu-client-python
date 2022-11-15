import argparse
import base64
import json
import os
import pprint

from common import setup_logging

from satellitevu.auth import Auth


def get_token(scope: str):
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("CLIENT_ID and CLIENT_SECRET must be set")

    auth = Auth(client_id=client_id, client_secret=client_secret)
    token = auth.token(scopes=scope.split(" "))

    header, claims, signature = token.split(".")
    header = json.loads(base64.b64decode(header))
    claims = json.loads(base64.b64decode(claims))

    print(f"=== Token for scope '{scope}' ===")
    print(token)
    print("\n=== Token Header ===")
    pprint.pprint(header)
    print("\n=== Token Claims ===")
    pprint.pprint(claims)
    print("\n=== Token Signature ===")
    pprint.pprint(signature)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", help="increase output verbosity", action="store_true"
    )
    parser.add_argument("--scope", help="scope to request", default="")

    args = parser.parse_args()
    setup_logging(args.verbose)

    get_token(args.scope)

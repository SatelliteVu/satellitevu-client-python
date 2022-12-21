#!/usr/bin/env python

from argparse import ArgumentParser
from re import compile
from subprocess import run
from sys import stderr

RULE = compile(r"^(?P<rule>(patch|minor|major))\/.*$")


def get_bump_rule(branch: str):
    match = RULE.match(branch)
    if match:
        return match.groupdict()["rule"]


def bump_version(rule):
    run(["poetry", "version", rule])
    return run(["poetry", "version", "-s"], capture_output=True, text=True)


def main(branch):
    rule = get_bump_rule(branch)
    if rule:
        new_version = bump_version(rule)
        print(f"NEW_VERSION={new_version.stdout}")
    else:
        print("No bump rule detected, skipping", file=stderr)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("branch")

    args = parser.parse_args()
    main(args.branch)

"""
Check code samples in a directory tree.

% mkdocs-codecheck ~/mySite/code-samples
"""

import argparse
import logging
import time
from dotenv import load_dotenv
from pathlib import Path

from .base import process_code

def main():
    p = argparse.ArgumentParser(description="Check code files within a directory or tree.")
    p.add_argument(
        "path",
        help="Path to code samples directory")
    p.add_argument(
        "-v", "--verbose",
        action="store_true")
    p.add_argument(
        "--exclude",
        help="a pattern for a file or path to exclude",
        action="append")
    p.add_argument(
        "-r", "--recurse",
        help="recurse directories under path",
        action="store_true")
    p.add_argument(
        "--dotenv",
        help="The path to a .env file that contains environment variables to pull into the current execution context")
    P = p.parse_args()

    if P.verbose:
        logging.basicConfig(level=logging.INFO)

    if P.dotenv:
        dotenv_path = Path( P.dotenv )
        load_dotenv(dotenv_path=dotenv_path)
        
    tic = time.monotonic()
    bad = process_code(
        P.path,
        recurse=P.recurse,
        exclude=P.exclude
    )

    print(f"{time.monotonic() - tic:0.3} seconds to check code samples")

    if bad:
        # using 22 following cURL
        # https://everything.curl.dev/usingcurl/returns
        print("Errors were discovered in your code samples. Exiting with an error.")
        raise SystemExit(22)


if __name__ == "__main__":
    main()

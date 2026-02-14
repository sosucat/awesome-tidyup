#!/usr/bin/env python3
"""Run `extract_tidyup` then `extract_access_scores` in sequence.

Usage (via project runner):
  pixi run python -m src.awesome_tidyup.run_all

The script calls the two modules' `main()` functions with the provided paths.
"""
from __future__ import annotations

import argparse
import sys
from typing import Callable


def _call_main(func: Callable, argv: list[str]) -> None:
    old_argv = sys.argv[:]
    try:
        sys.argv[:] = argv
        func()
    finally:
        sys.argv[:] = old_argv


def main() -> None:
    p = argparse.ArgumentParser(description="Run extract_tidyup then extract_access_scores")
    p.add_argument("-i", "--tidyup-input", default="data/input_tidyup", help="input dir or file for tidyup (default: data/input_tidyup)")
    p.add_argument("-o", "--tidyup-output", default="tidyup_list.csv", help="output tidyup CSV (default: tidyup_list.csv)")
    p.add_argument("-a", "--access-input", default="data/input_access", help="input dir for access HTML files (default: data/input_access)")
    p.add_argument("-s", "--access-output", default="access_scores.csv", help="output merged CSV (default: access_scores.csv)")
    args = p.parse_args()

    print(f"Running extractor: input={args.tidyup_input} -> output={args.tidyup_output}")
    # import here to avoid import-time side-effects
    from src.awesome_tidyup import extract_tidyup

    _call_main(extract_tidyup.main, ["extract_tidyup", "-i", args.tidyup_input, "-o", args.tidyup_output])

    print(f"Running access-scores merger: input={args.access_input} tidyup={args.tidyup_output} -> output={args.access_output}")
    from src.awesome_tidyup import extract_access_scores

    _call_main(extract_access_scores.main, ["extract_access_scores", "-i", args.access_input, "-t", args.tidyup_output, "-o", args.access_output])

    print("Done: tidyup and access scores generated.")


if __name__ == "__main__":
    main()

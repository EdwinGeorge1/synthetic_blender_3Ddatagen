#!/usr/bin/env python3

import sys, os

# 1) Make sure project root is on Python’s import path
root = os.path.dirname(os.path.abspath(__file__))
if root not in sys.path:
    sys.path.insert(0, root)

import argparse
from primitives import get_wrapper

def parse_args():
    argv = sys.argv
    # If called under Blender: split on the '--' Blender-to-script separator
    if "--" in argv:
        idx = argv.index("--")
        cli_args = argv[idx+1:]
    else:
        # If called directly via Python (for testing), take everything after script name
        cli_args = argv[1:]

    p = argparse.ArgumentParser(
        description="Wrap an image onto a chosen primitive"
    )
    p.add_argument(
        "-p","--primitive",
        choices=['box','cylinder'],
        default='box',
        help="Which primitive to wrap"
    )
    p.add_argument(
        "-i","--image", required=True,
        help="Path to image file"
    )
    p.add_argument(
        "-o","--outdir", required=True,
        help="Output directory"
    )
    return p.parse_args(cli_args)

def main():
    args = parse_args()
    get_wrapper(args.primitive).run(args.image, args.outdir)

if __name__=="__main__":
    main()

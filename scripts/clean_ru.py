#!/usr/bin/env python3

import argparse
import re
import sys


def norm_text(text):
    return " ".join([j for j in (t.strip() for t in re.split('[^а-яА-Я]', text)) if j])


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--input", "-i", type=str, required=True)
    par.add_argument("--output", '-o', type=str, default=None)
    args = par.parse_args(sys.argv[1:])
    input = args.input
    output = args.output or f'{input}.clean'
    open(output, 'w').write(norm_text(open(input, 'r').read()))

#!/usr/bin/env python3

import argparse
import sys
from pymystem3 import Mystem


def get_s(text):
    stemmer = Mystem()
    analyzed = stemmer.analyze(text)
    return " ".join([x['text'] for x in analyzed if
                     ((x['analysis'][0]['gr'][0] == 'S') if ('analysis' in x and len(x['analysis']) > 0) else False)])


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--input", "-i", type=str, required=True)
    par.add_argument("--output", '-o', type=str, default=None)
    args = par.parse_args(sys.argv[1:])
    input = args.input
    output = args.output or f'{input}.clean'
    open(output, 'w').write(get_s(open(input, 'r').read()))

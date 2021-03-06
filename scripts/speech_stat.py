#!/usr/bin/env python3

import argparse
import logging
import os
import sys

import collections
from pymystem3 import Mystem
from nltk.corpus import stopwords


logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger("word_stat")
log.setLevel(logging.DEBUG)
stemmer = Mystem()


def lemm(text):
    return list(filter(lambda x: x, map(lambda x: x.strip(), stemmer.lemmatize(text.lower()))))


def freq(it):
    r = collections.defaultdict(int)
    for i in it:
        r[i] += 1
    return dict(r)


def keywords(text, remove_commons=True):
    normal_words = lemm(text)
    if remove_commons:
        normal_stop_words = lemm(" ".join(set(stopwords.words('russian'))) + " . ! ,")
        filtered_words = list(filter(lambda x: not x in normal_stop_words, normal_words))
    else:
        filtered_words = list(normal_words)
    words = [j for j in [i.strip(' .!?"-\u2026,_') for i in filtered_words] if j]
    print(words)
    return freq(words)


def calc_stat(input_name, output_name, redo=False, remove_commons=True):
    if not redo:
        if os.path.exists(output_name): return
    text = open(input_name, "r").read().strip()
    kw = keywords(text, remove_commons=remove_commons)
    open(output_name, 'w').write("\n".join([f'{i} {v}' for i, v in kw.items()]))


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--input", '-i', type=str, default='tmp.txt')
    par.add_argument("--output", '-o', type=str, default='tmp.stat')
    par.add_argument("--redo", action="store_true")
    par.add_argument("--leave-common", "-c", action="store_true")
    args = par.parse_args(sys.argv[1:])
    log.debug(f"stat for '{args.input}'")
    calc_stat(args.input, args.output or f"{args.input}.stat", redo=args.redo, remove_commons=not args.leave_common)

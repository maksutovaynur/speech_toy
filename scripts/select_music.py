#!/usr/bin/env python3

import argparse
import os
import sys
import math
import logging

log = logging.getLogger("select_music")
log.setLevel(logging.DEBUG)
logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)])


from list_music import list_from_dir


def stat_read(file_name):
    return {j[0]: int(j[1]) for j in [i.split(" ", 1) for i in open(file_name, 'r').read().strip().split("\n")]}


def norm_stat(kw):
    sm = math.sqrt(sum(map(lambda x: x * x, kw.values())))
    if sm == 0: return {}
    return {i: v / sm for i, v in kw.items()}


def distance(seq1, seq2):
    n, m = len(seq1), len(seq2)
    if n > m: seq1, seq2, n, m = seq2, seq1, m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if seq1[j - 1] != seq2[i - 1]: change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def multiply2stats(stat1, stat2, max_dist=2):
    res = {}
    for i, v in stat1.items():
        if max_dist > 0:
            for ii, vv in stat2.items():
                d = distance(i, ii)
                if d <= max_dist:
                    res[(i, ii)] = v * vv
            continue
        vv = stat2.get(i, None)
        if vv is None: continue
        res[(i, i)] = vv * v
    return res


def sum_stat(kw):
    return sum(kw.values())


def text_read(file_name):
    return open(file_name, 'r').read().strip()


def crop_list(lst, dim_factor=0.9, max_sec=5):
    current = lst[0]
    i = 0
    for i, v in enumerate(lst[1:max_sec]):
        if current == 0: return i
        if v/current < dim_factor: return i + 1
    return i + 2


if __name__ == "__main__":
    base_path = os.path.join(os.path.dirname(__file__), os.path.pardir)
    par = argparse.ArgumentParser()
    par.add_argument("--speech-text-file", "-t", type=str, default='tmp.txt')
    par.add_argument("--speech-stat-file", "-s", type=str, default='tmp.stat')
    par.add_argument("--stat-file", "-dd", type=str, default=None)
    par.add_argument("--stat-dir", "-d", type=str, default=os.path.join(base_path, "recognized_stat"))
    par.add_argument("--stat-format", "-f", type=str, default='stat')
    par.add_argument("--dim-factor", "-g", type=float, default=0.7)
    par.add_argument("--max-seq", "-m", type=int, default=5)
    par.add_argument("--output", "-o", type=str, default='tmp.cand')
    args = par.parse_args(sys.argv[1:])
    if args.stat_file is None:
        names = list_from_dir(args.stat_dir, args.stat_format)
    else:
        names = open(args.stat_file, 'r').read().strip().split("\n")
    # log.debug(f"names {names}")
    texts = {i: stat_read(os.path.join(args.stat_dir, i)) for i in names}
    # log.debug(f"texts {texts}")
    nsp = norm_stat(stat_read(args.speech_stat_file))
    scores = sorted([(i, sum_stat(multiply2stats(nsp, norm_stat(v)))) for i, v in texts.items()], key=lambda x: - x[1])
    print(f"You entered: '{text_read(args.speech_text_file)}'")
    best = scores[:crop_list([x[1] for x in scores], dim_factor=args.dim_factor, max_sec=args.max_seq)]
    # print(best)
    open(args.output, 'w').write("\n".join(".".join(x[0].split(".", 2)[:2]) for x in best))
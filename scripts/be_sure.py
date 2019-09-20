#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
from generate_speech import norm_text

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

def sc(sc):
    return f"./scripts/{sc}"

def r(sc):
    return f"artefacts/{sc}"


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--input", "-i", type=str, default='tmp.cand')
    par.add_argument("--output", "-o", type=str, default='tmp.choice')
    # par.add_argument("--music", "-m", type=str, default="music")
    args = par.parse_args(sys.argv[1:])
    initial_lst = open(args.input, 'r').read().strip().split("\n")
    lst = [norm_text(i) for i in initial_lst]
    print("lst: ", lst)
    if len(lst) > 1:
        choices = [norm_text(l.split("-", 1)[-1]) for l in initial_lst]
        choice_names = [f"music_names/{i}.wav" for i in choices]
        print(f"CHOICE NAMES: {choice_names}")
        for c, n in zip(choices, choice_names):
            subprocess.call([sc('generate_speech.py'), "--redo", "-t", f"'{c}'", "-o", n])
        os.system("mplayer -speed 1.3 sounds_synt/options.wav")
        os.system("mplayer -speed 1.3 " + " sounds_synt/or.wav ".join([f"'{c}'" for c in choice_names]))
        os.system(f"{sc('record_speech.py')} -d 0 -t 3 -o {r('tmp.choice.result.wav')}")
        os.system(f"{sc('speech_reco.py')} --redo -i {r('tmp.choice.result.wav')} -o {r('tmp.choice.result.reco')}")
        os.system(f"{sc('speech_stat.py')} --redo -i {r('tmp.choice.result.reco')} -o {r('tmp.choice.result.stat')}")
        os.system(f"{sc('select_music.py')} -t {r('tmp.choice.result.reco')} -s {r('tmp.choice.result.stat')}"
                  f" -d music_names -f rec.stat -m 100 -g 0 -o {r('tmp.choice_all')}")
        for i in open(r('tmp.choice_all'), 'r').read().strip().split("\n"):
            # print(norm_text(i))
            if norm_text(i) in lst:
                open(args.output, 'w').write(i)
                print(i)
                exit(0)
    elif len(lst) == 1:
        open(args.output, 'w').write(initial_lst[0])

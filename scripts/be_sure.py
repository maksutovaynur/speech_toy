#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess as S
from generate_speech import norm_text

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

def sc(sc):
    return f"./scripts/{sc}"

def r(sc):
    return f"artefacts/{sc}"


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--input", "-i", type=str, default='artefacts/request.cand')
    par.add_argument("--output", "-o", type=str, default='artefacts/request.choice')
    par.add_argument("--artefacts-dir", "-a", type=str, default='artefacts')
    par.add_argument("--speech-options", "-so", type=str, default='sounds_synt/options.wav')
    par.add_argument("--speech-connection", "-sc", type=str, default='sounds_synt/or.wav')
    par.add_argument("--music-names-dir", "-md", type=str, default='music_names')
    par.add_argument("--music-names-stat-ext", "-me", type=str, default='.res.stat')
    # par.add_argument("--music", "-m", type=str, default="music")
    args = par.parse_args(sys.argv[1:])

    F_i = args.input
    F_o = args.output
    D_mn = args.music_names_dir
    E_mn = args.music_names_stat_ext
    Sp_opt = args.speech_options
    Sp_or = args.speech_connection
    S_tts = "scripts/generate_speech.py"
    S_stt = "scripts/speech_reco.py"
    S_rec = "scripts/record_speech.py"
    S_stat = "scripts/speech_stat.py"
    S_sel = "scripts/select_music.py"

    music_names = open(F_i, 'r').read().strip().split("\n")
    spoken_music_names = [norm_text(i) for i in music_names]

    print("lst: ", spoken_music_names)
    if len(spoken_music_names) > 1:
        choices = [norm_text(l.split("-", 1)[-1]) for l in music_names]
        choice_names = [f"music_names/{i}.wav" for i in choices]
        pr = []
        for c, n in zip(choices, choice_names):
            pr.append(S.Popen([S_tts, "--redo", "-t", f"'{c}'", "-o", n], stdout=S.PIPE))
        os.system(f"mplayer -speed 1.2 {Sp_opt}")
        for p in pr: p.stdout.read()
        os.system("mplayer -speed 1.2 " + f" {Sp_or} ".join([f"'{c}'" for c in choice_names]))
        os.system(f"{S_rec} -d 0 -t 3 -o {F_o}.res.wav")
        os.system(f"{S_stt} --redo -i {F_o}.res.wav -o {F_o}.res.txt")
        os.system(f"{S_stat} --redo -i {F_o}.res.txt -o {F_o}.res.stat -c")
        os.system(f"{S_sel} -t {F_o}.res.txt -s {F_o}.res.stat -d {D_mn} -f {E_mn} -m 100 -g 0 -o {F_o}.res.all -f rec.stat")
        for i in open(f"{F_o}.res.all", 'r').read().strip().split("\n"):
            if norm_text(i) in spoken_music_names:
                open(F_o, 'w').write(i)
                print(i)
                exit(0)
    elif len(spoken_music_names) == 1:
        open(F_o, 'w').write(music_names[0])

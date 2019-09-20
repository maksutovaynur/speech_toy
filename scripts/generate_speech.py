#!/usr/bin/env python3

import argparse
import os
import re
import sys
# import requests
# from speech_reco import get_header

from gtts import gTTS


def generate_speech(text, output_name, redo=False, lang='ru', **kwargs):
    if not redo:
        if os.path.exists(output_name): return
    tts = gTTS(text, lang=lang)
    tts.save(output_name)


# YDX_SPEECH_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize?lang=ru-RU&voice=ermil&" \
#                  "emotion=good&speed=1.5&format=oggopus&sampleRateHertz={rate}&text={text}"
#
#
# def ydx_generate(text, rate=8000, output_name="", cache_folder=""):
#     wtext = " ".join([j for j in (t.strip() for t in re.split('[^а-яА-Я]', text)) if j])
#     cached_file_name = os.path.join(cache_folder, wtext, ".ogg")
#     if not os.path.exists(cached_file_name):
#         res = requests.post(YDX_SPEECH_URL.format(text=text, rate=rate), headers=get_header())
#         if res.status_code == 200:
#             print(res)

def norm_text(text):
    return " ".join([j for j in (t for t in re.split('[^а-яА-Я]', text)) if j])


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--input-file", "-i", type=str, default=None)
    par.add_argument("--output", '-o', type=str, required=True)
    par.add_argument("--input-text", '-t', type=str, default=None)
    par.add_argument("--redo", action="store_true")
    base_folder = os.path.join(os.path.dirname(__file__), os.path.pardir)
    # par.add_argument("--cache-folder", "-c", default=os.path.join(base_folder, "sounds_synt"))
    args = par.parse_args(sys.argv[1:])
    if args.input_text is not None:
        text = args.input_text
    elif args.input_file is not None:
        text = open(args.input_file, 'r').read().strip()
    else: exit(0)
    wtext = norm_text(text)
    generate_speech(text=wtext, output_name=args.output, redo=args.redo)
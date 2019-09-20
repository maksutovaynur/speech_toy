#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import requests
import pydub

logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger("speech_reco")
log.setLevel(logging.DEBUG)


YDX_STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize" \
              "?lang=ru-RU&topic=general&profanityFilter=true&format=oggopus"

YDX_SECRET_KEY = None
YDX_SECRET_FILE_NAME = os.path.join(os.path.dirname(__file__), "yandex_api_key")


def ydx_secret_key_lazy():
    global YDX_SECRET_KEY
    global YDX_SECRET_FILE_NAME
    if YDX_SECRET_KEY is None:
        ydx_data = open(YDX_SECRET_FILE_NAME, "r").read().strip().split("\n")
        ydx_json = {j[0]: j[1] for j in [i.strip().split("=", 1) for i in ydx_data] if len(j) == 2}
        YDX_SECRET_KEY = ydx_json.get('SECRET_KEY', None)
    return YDX_SECRET_KEY


def get_header():
    return {"Authorization": f"Api-Key {ydx_secret_key_lazy()}"}


def request_yand_tts(audio_part_binary):
    res = requests.post(YDX_STT_URL, headers=get_header(), data=audio_part_binary)
    if res.status_code == 200:
        text = res.json()['result']
        log.debug(f"successfully recognized a part:\n{text}")
        return text
    else:
        log.error(f"error while recognizing part")
        return None


def do_recognition(file_name):
    try:
        s = pydub.AudioSegment.from_wav(file_name)
    except Exception as e:
        log.error(f"While reading wav: {e}")
        try: s = pydub.AudioSegment.from_mp3(file_name)
        except Exception as e:
            log.error(f"While reading mp3: {e}")
            s = pydub.AudioSegment.from_file(file_name, format='ogg')
    parts = pydub.utils.make_chunks(s, chunk_length=14400)
    ress = [request_yand_tts(p.export(format="ogg", codec="libopus").read()) for p in parts]
    return " ".join(filter(lambda x: isinstance(x, str), ress))


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--input", "-i", type=str, default="tmp.wav")
    par.add_argument("--output", "-o", type=str, default="tmp.txt")
    par.add_argument("--redo", action="store_true")
    args = par.parse_args(sys.argv[1:])

    output_name = args.output
    log.info(f"recognize '{args.input}'?")
    if output_name is None: output_name = f'{args.input}.rec'
    if not args.redo:
        if os.path.exists(output_name):
            exit(0)
    log.info("start recognition")
    speech = do_recognition(args.input)
    open(output_name, 'w').write(speech + "\n")

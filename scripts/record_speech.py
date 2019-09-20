#!/usr/bin/env python3

import argparse
import logging
import sys
import os

import speech_recognition as sr

log = logging.getLogger("voice_record")
logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)])
log.setLevel(logging.DEBUG)


def record_speech(device_index, time_limit, output_name):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index=device_index)

    log.info("Measure noise")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    log.info("Start recording")
    os.system("mplayer -speed 1.3 sounds_synt/start.wav")
    with microphone as source:
        audio = recognizer.listen(source, phrase_time_limit=time_limit)
    log.info("Stop recording")
    os.system("mplayer -speed 1.3 sounds_synt/end.wav")
    open(output_name, 'wb').write(audio.get_wav_data())


if __name__ == "__main__":
    par = argparse.ArgumentParser()
    par.add_argument("--device", "-d", type=int, default=0)
    par.add_argument("--output", "-o", type=str, required=True)
    par.add_argument("--time-limit", "-t", type=int, default=2)

    args = par.parse_args(sys.argv[1:])

    record_speech(args.device, args.time_limit, args.output)


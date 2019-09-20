#!/usr/bin/env bash

./scripts/record_speech.py -d 0 -o tmp.wav -t 4  \
&& ./scripts/speech_reco.py --redo \
&& ./scripts/speech_stat.py --redo \
&& ./scripts/select_music.py \
&& ./scripts/be_sure.py -o tmp.choice \
&& cat tmp.choice | xargs -I{} mpg123 'music/{}'

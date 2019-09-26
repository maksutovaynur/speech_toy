#!/usr/bin/env bash

./scripts/record_speech.py -d 0 -o artefacts/request.wav -t 4  \
&& ./scripts/speech_reco.py -i artefacts/request.wav -o artefacts/request.txt --redo \
&& ./scripts/speech_stat.py -i artefacts/request.txt -o artefacts/request.stat --redo -c \
&&
./scripts/select_music.py -t artefacts/request.txt -s artefacts/request.stat -o artefacts/request.cand -f reco.stat \
&&
./scripts/be_sure.py -i artefacts/request.cand -o artefacts/request.choice \
&&
cat artefacts/request.choice | xargs -I{} mplayer 'music/{}'

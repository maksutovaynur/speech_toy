import io
import logging
import sys
from os import path
import time
import pydub
import requests
import simpleaudio
from gtts import gTTS
from pymystem3 import Mystem
from speech_recognition import Recognizer, Microphone, AudioData, AudioFile
logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger("voice_tools")
log.setLevel(logging.DEBUG)
rec = Recognizer()
EXSPEECH = {}
MIC_RATE = 48000
import pyaudio
p = pyaudio.PyAudio()

# open stream (2)
mic = Microphone(sample_rate=MIC_RATE)

stemmer = Mystem()


def load_music(filename):
    with AudioFile(filename) as source:
        return rec.record(source)


def save_audio(audio: AudioData, file_name):
    open(file_name, 'wb').write(audio.get_wav_data(audio.sample_rate, audio.sample_width))


def adjust_noise(seconds=2, mic=mic):
    with mic as m:
        rec.adjust_for_ambient_noise(m, duration=seconds)


def speed_change(sound, speed=1.0):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)})
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)


SOUNDS = path.join(path.dirname(__file__), path.pardir, 'sounds')


def get_sound_path(name):
    return path.join(SOUNDS, f"{name}.wav")


def gen_speech(text, lang='ru'):
    global EXSPEECH
    ex = EXSPEECH.get(text, None)
    if ex is None:
        fname = get_sound_path(text)
        if not path.exists(fname):
            tts = gTTS(text, lang=lang)
            res = io.BytesIO()
            tts.write_to_fp(res)
            res.seek(0)
            mp3 = pydub.AudioSegment.from_mp3(res)
            res = io.BytesIO()
            mp3.export(res, format='wav')
            res.seek(0)
            with AudioFile(res) as s:
                ex = rec.record(s)
            res.seek(0)
            open(fname, 'wb').write(res.read())
        else:
            with AudioFile(fname) as s:
                ex = rec.record(s)
        EXSPEECH[text] = ex
    return ex


def get_player(audio: AudioData, speed=1.2):
    wavdata = audio.get_wav_data(convert_rate=audio.sample_rate, convert_width=audio.sample_width)
    data = speed_change(pydub.AudioSegment.from_wav(io.BytesIO(wavdata)), speed)
    pl = simpleaudio.play_buffer(data.raw_data, data.channels, data.sample_width, data.frame_rate)
    return pl


YDX_STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize" \
              "?lang=ru-RU&topic=general&profanityFilter=true&format=oggopus"

YDX_SECRET_KEY = None
YDX_SECRET_FILE_NAME = path.join(path.dirname(__file__), "yandex_api_key")


def get_header():
    return {"Authorization": f"Api-Key {ydx_secret_key_lazy()}"}


def yandex_recognize(audio: AudioData):
    data = io.BytesIO()
    pydub.AudioSegment.from_wav(io.BytesIO(audio.get_wav_data(audio.sample_rate, audio.sample_width))) \
        .export(data, format='ogg')
    data.seek(0)
    res = requests.post(YDX_STT_URL, headers=get_header(), data=data.read())
    if res.status_code == 200:
        text = res.json()['result']
        log.debug(f"successfully recognized a part:\n{text}")
        return text
    else:
        log.error(f"error while recognizing part")
        return None


def sphinx_recognize(audio, kw=None):
    return rec.recognize_sphinx(audio, language='ru', keyword_entries=kw)


def ydx_secret_key_lazy():
    global YDX_SECRET_KEY
    global YDX_SECRET_FILE_NAME
    if YDX_SECRET_KEY is None:
        ydx_data = open(YDX_SECRET_FILE_NAME, "r").read().strip().split("\n")
        ydx_json = {j[0]: j[1] for j in [i.strip().split("=", 1) for i in ydx_data] if len(j) == 2}
        YDX_SECRET_KEY = ydx_json.get('SECRET_KEY', None)
    return YDX_SECRET_KEY


def listen(time_limit=2, mic=mic):
    log.info("Start recording")
    # with mic as source:
    #     audio = rec.listen(source, phrase_time_limit=time_limit)
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=MIC_RATE,
                    input=True,
                    frames_per_buffer=MIC_RATE*1)
    audio = AudioData(stream.read(time_limit*MIC_RATE), sample_rate=MIC_RATE, sample_width=2)
    # with  as source:
    #     audio = rec.record(source)
    log.info("Stop recording")
    stream.stop_stream()
    stream.close()

    return audio


if __name__=="__main__":
    audio = listen(2)
    print(audio)
    if audio is None: exit(0)
    p = get_player(audio, 1.2)
    save_audio(audio, 'tmp.wav')
    time.sleep(0.5)
    p.stop()
    time.sleep(1)
    p.wait_done()
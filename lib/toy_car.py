import multiprocessing as P
from datetime import datetime
from os import path
from lib import wifitools as W


from lib import voice_tools as V
from lib import stats as S
import subprocess as SP


def recognize_parallel(audio, texts):
    res = V.yandex_recognize(audio)
    if res is not None:
        if res.strip() != '':
            texts.put(res)


BASE_NAME = path.join(path.dirname(__file__), path.pardir)
MUSIC_DIR = path.join(BASE_NAME, 'music')
MUSIC_STAT_DIR = path.join(BASE_NAME, 'recognized_stat')


def text_processor(texts: P.Queue, ip: str):
    Left, Right, Fwd = ['лево', 'налево'], ['вправо', 'направо', 'право'], ['дрифт', 'круг', 'поехали', 'вперёд', 'перед']
    Stop = ['стоп', 'хватит', 'хорош']
    Left, Right, Fwd, Stop = [[S.lemm(w)[0] for w in j] for j in (Left, Right, Fwd, Stop)]
    LeftS, RightS, FwdS, StopS = set(Left), set(Right), set(Fwd), set(Stop)
    while True:
        m = texts.get()
        ms = []
        while True:
            try: v = texts.get_nowait()
            except: v = None
            if v is None: break
            ms.append(v)
        t = " ".join([m] + ms)
        if len(t.strip()) == 0: continue
        l = S.lemm(t).split(" ")
        print(f"You said (nomalized): {l}")
        ls = set(l)
        if len(ls & LeftS) > 0:
            W.send_cmd(ip, 'N')
            SP.Popen(['mplayer', '-speed', '0.8', V.get_sound_path('еду влево')])
        elif len(ls & RightS) > 0:
            W.send_cmd(ip, 'P')
            SP.Popen(['mplayer', '-speed', '0.8', V.get_sound_path('еду вправо')])
        elif len(ls & FwdS) > 0:
            W.send_cmd(ip, '1')
            SP.Popen(['mplayer', '-speed', '0.8', V.get_sound_path('дрифтую')])
        elif len(ls & LeftS) > 0:
            W.send_cmd(ip, 'f')
            SP.Popen(['mplayer', '-speed', '0.8', V.get_sound_path('стою')])


def init_phrases():
    phrases = [
        'привет',
        # 'поняла',
        # 'как тебя зовут?',
        'я умею ездить, командуй',
        # 'какую песенку спеть?',
        'еду влево',
        'еду вправо',
        'дрифтую',
        'стою',
    ]
    for p in phrases:
        V.gen_speech(p)
    pass


if __name__=="__main__":
    import sys
    ip = sys.argv[1] if len(sys.argv) > 0 else None
    # print(V.Microphone.list_microphone_names())
    # mic = V.Microphone(sample_rate=V.MIC_RATE)
    init_phrases()

    V.get_player(V.gen_speech('привет'), speed=0.8).wait_done()

    # V.adjust_noise(2)
    V.get_player(V.gen_speech('я умею ездить, командуй'), speed=0.8).wait_done()

    texts = P.Queue(maxsize=1024)
    lock = P.Lock()
    worker = P.Process(target=text_processor, kwargs=dict(texts=texts, lock=lock, ip=ip))
    worker.start()
    try:
        while True:
            with lock:
                audio = V.listen(2)
            if audio is None: continue
            open('request.wav', 'wb').write(audio.get_wav_data(audio.sample_rate, audio.sample_width))
            p = P.Process(target=recognize_parallel, kwargs=dict(audio=audio, texts=texts))
            p.start()
            print(datetime.now())
    except KeyboardInterrupt: pass

    worker.join()

import multiprocessing as P
from lib.stats import distance
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


def text_processor(texts: P.Queue, lock: P.Lock, ip: str):
    while True:
        m = texts.get()
        ms = []
        while True:
            try: v = texts.get_nowait()
            except: v = None
            if v is None: break
            ms.append(v)
        t = " ".join([m] + ms)

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


SPEECH_SPEED = 1.3


def levenst(lst1, lst2):
    return min(distance(l1, l2) for l1 in lst1 for l2 in lst2)


if __name__=="__main__":
    import sys
    ip = sys.argv[1] if len(sys.argv) > 0 else None
    init_phrases()

    V.get_player(V.gen_speech('привет'), speed=SPEECH_SPEED).wait_done()
    V.get_player(V.gen_speech('я умею ездить, командуй'), speed=SPEECH_SPEED).wait_done()
    Left, Right, Fwd = ['лево', 'налево', 'слева', 'слово'], \
                       ['вправо', 'направо', 'право', 'справа', 'правда'], \
                       ['дрифт', 'круг', 'поехали', 'вперёд', 'перед', 'прямо']
    Stop = ['стоп', 'хватит']
    Left, Right, Fwd, Stop = [[S.lemm(w)[0] for w in j] for j in (Left, Right, Fwd, Stop)]
    LeftS, RightS, FwdS, StopS = set(Left), set(Right), set(Fwd), set(Stop)
    try:
        while True:
            # with lock:
            audio = V.listen(0.9)
            if audio is None: continue
            open('request.wav', 'wb').write(audio.get_wav_data(audio.sample_rate, audio.sample_width))
            t = V.yandex_recognize(audio)
            if len(t.strip()) == 0: continue
            l = S.lemm(t)
            print(f"You said (nomalized): {l}")
            ls = set(l)
            to_sel = [('N', list(LeftS), 'еду влево'),
                      ('P', list(RightS), 'еду вправо'),
                      ('1', list(FwdS), 'дрифтую'),
                      ('f', list(Stop), 'стою')]
            to_sel_calc = sorted([(i, levenst(l, a), x) for i, a, x in to_sel], key=lambda x: x[1])
            if to_sel_calc[0][1] > 4:
                command, sound = 'f', 'стою'
            else:
                command, sound = to_sel_calc[0][0], to_sel_calc[0][2]

            SP.Popen(['mplayer', '-speed', str(SPEECH_SPEED), V.get_sound_path(sound)]).wait()
            W.send_cmd(ip, command)
    except KeyboardInterrupt: pass

    # worker.join()

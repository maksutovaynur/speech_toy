import multiprocessing as P
from datetime import datetime
from os import path, listdir


from lib import voice_tools as V
from lib import stats as S


def recognize_parallel(audio, texts):
    res = V.yandex_recognize(audio)
    if res is not None:
        if res.strip() != '':
            texts.put(res)


BASE_NAME = path.join(path.dirname(__file__), path.pardir)
MUSIC_DIR = path.join(BASE_NAME, 'music')
MUSIC_STAT_DIR = path.join(BASE_NAME, 'recognized_stat')


def list_music_names():
    stats = set(x.split(".", 1)[0] for x in listdir(MUSIC_STAT_DIR) if x.endswith('.reco.stat'))
    music = set(x.split(".", 1)[0] for x in listdir(MUSIC_DIR) if x.endswith('.mp3'))
    common = stats & music
    return list(common)


def get_music_path(name):
    return path.join(MUSIC_DIR, f"{name}.mp3")


def get_stat_path(name):
    return path.join(MUSIC_STAT_DIR, f"{name}.mp3.reco.stat")


def stat_read(file_name):
    text = open(file_name, 'r').read().split("\n")
    try:
        return {j[0]: int(j[1]) for j in [i.split(" ", 1) for i in text] if len(j) > 1}
    except Exception as e:
        print(f"err with TEXT <{text}>: {e}")


import subprocess as SP


def text_processor(texts: P.Queue, lock: P.Lock):
    state = 'initial'
    start_words = ['песня', 'песенка', 'включить', 'включать']
    stop_words = ['выключить', 'выключать', 'стоп', 'хватит', 'хватать', 'хватить', 'молчать', 'замолчать',
                  'дура', 'придурок', 'стоять', 'хорошо', 'хороший']
    start_words = [S.lemm(w)[0] for w in start_words]
    stop_words = [S.lemm(w)[0] for w in stop_words]
    print(start_words, stop_words)
    music_names = list_music_names()
    stat_path = {i: get_stat_path(i) for i in music_names}

    Stats = {i: stat_read(v) for i, v in stat_path.items()}
    normStats = {i: S.norm_stat(v) for i, v in Stats.items()}
    Play = None
    MusicPlay = None
    while True:
        if Play is not None:
            if state != 'song':
                Play.stop()
                Play = None
        m = texts.get()
        ms = []
        while True:
            try: v = texts.get_nowait()
            except: v = None
            if v is None: break
            ms.append(v)
        t = " ".join([m] + ms)
        if len(t.strip()) == 0: continue
        l = S.lemm(t)
        print(f"You said (nomalized): {l}")
        if state == 'initial':
            for w in start_words:
                if w in l:
                    state = 'select'
                    voice = V.gen_speech('какую песенку спеть?')
                    # with lock:
                    V.save_audio(voice, 'voice.wav')
                    # v = V.get_player(voice)
                    # v.wait_done()
                    with lock:
                        p = SP.Popen(['mplayer', '-speed', '1.2', 'voice.wav'])
                        p.wait()
                    break
        elif state == 'select':
            kw = S.norm_stat(S.keywords(l, remove_commons=False))
            vals =  sorted([(i, S.sum_stat(S.multiply2stats(kw, s))) for i, s in normStats.items()], key=lambda x: -x[1])
            music_name = get_music_path(vals[0][0])
            MusicPlay = SP.Popen(['mplayer', music_name])
            # music = V.load_music()
            # Play = V.get_player(music)
            state = 'song'

        elif state == 'song':
            for w in stop_words:
                if w in l:
                    state = 'initial'
                    if MusicPlay is not None:
                        MusicPlay.kill()
                    break


def init_phrases():
    phrases = [
        'привет',
        'поняла',
        'как тебя зовут?',
        'я умею петь песенки, если попросишь',
        'какую песенку спеть?',
    ]
    for p in phrases:
        V.gen_speech(p)
    pass


if __name__=="__main__":
    # print(V.Microphone.list_microphone_names())
    # mic = V.Microphone(sample_rate=V.MIC_RATE, device_index=V.Microphone.list_microphone_names().index('sysdefault'))
    init_phrases()
    V.adjust_noise(2)
    V.get_player(V.gen_speech('как тебя зовут?')).wait_done()
    name = None
    while name is None:
        audio = V.listen(2)
        if audio is None: continue
        name = V.yandex_recognize(audio)
        if isinstance(name, str) and len(name.strip())==0:
            name = None

    p = V.get_player(V.gen_speech('поняла'))
    name_audio = V.gen_speech(name)
    p.wait_done()

    V.get_player(V.gen_speech('привет')).wait_done()
    V.get_player(name_audio).wait_done()

    V.get_player(V.gen_speech('я умею петь песенки, если попросишь')).wait_done()

    texts = P.Queue(maxsize=1024)
    lock = P.Lock()
    worker = P.Process(target=text_processor, kwargs=dict(texts=texts, lock=lock))
    worker.start()
    try:
        while True:
            with lock:
                audio = V.listen(2)
            if audio is None:continue
            open('request.wav', 'wb').write(audio.get_wav_data(audio.sample_rate, audio.sample_width))
            p = P.Process(target=recognize_parallel, kwargs=dict(audio=audio, texts=texts))
            p.start()
            print(datetime.now())
    except KeyboardInterrupt: pass

    worker.join()

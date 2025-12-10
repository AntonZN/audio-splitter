import essentia
import essentia.standard as es


def analyze_audio(
    filepath: str,
    onset_type: str = "complex",
    sample_rate: int = 44100,
    frame_size: int = 2048,
    hop_size: int = 512,
):
    # 1. Загружаем аудио в моно
    audio = es.MonoLoader(filename=filepath, sampleRate=sample_rate)()

    # 2. BPM и биты
    # method='multifeature' обычно даёт наиболее устойчивый результат
    rhythm = es.RhythmExtractor2013(method="multifeature")
    bpm, beats, beat_confidence, bpm_estimates, bpm_intervals = rhythm(audio)
    # 3. Тональность (key)
    key_extractor = es.KeyExtractor()
    key, scale, key_strength = key_extractor(audio)
    # key – например 'C', 'G#', scale – 'major' или 'minor'

    # 4. Онсет-детекция
    # Шаг 1: считаем onset detection function по кадрам
    od = es.OnsetDetection(method=onset_type)  # можно попробовать 'hfc' / 'flux'

    window = es.Windowing(type="hann")
    fft = es.FFT()
    c2p = es.CartesianToPolar()

    pool = essentia.Pool()

    for frame in es.FrameGenerator(
            audio,
            frameSize=frame_size,
            hopSize=hop_size,
            startFromZero=True,
    ):
        mag, phase = c2p(fft(window(frame)))
        odf_value = od(mag, phase)
        pool.add("odf.complex", odf_value)

    # Шаг 2: по ODF находим сами онсеты (время в секундах)
    onsets = es.Onsets()
    onset_times = onsets(
        essentia.array([pool["odf.complex"]]),  # матрица ODF (1 x N)
        [1.0],  # веса (одна ODF → вес 1)
    )

    return {
        "bpm": float(bpm),
        "beats": [float(t) for t in beats],  # таймкоды битов, с
        "key": str(key),  # например 'G'
        "scale": str(scale),  # 'major' / 'minor'
        "onsetSsec": [float(t) for t in onset_times],  # таймкоды онсетов, с
    }


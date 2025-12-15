from typing import List

import essentia
import essentia.standard as es
import numpy as np

from BeatNet.BeatNet import BeatNet

from app.api.schemas import BeatNetResult


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
        "onsetsSec": [float(t) for t in onset_times],  # таймкоды онсетов, с
    }


def analyze_with_beatnet_offline(path: str) -> BeatNetResult:
    """
    Оффлайн-анализ трека BeatNet'ом + построение сетки для метронома.
    """

    # модель 1, offline, не рисуем графики
    estimator = BeatNet(
        model=1,
        mode="offline",
        inference_model="DBN",  # для offline автор рекомендует DBN
        plot=[],
        thread=False,
        device="cpu",  # либо "cuda", если есть
    )

    # Output: numpy_array(num_beats, 2) → [time, downbeat_flag]
    output = estimator.process(path)
    # output.shape: (N, 2)

    beat_times = output[:, 0].astype(float).tolist()
    downbeat_times = output[output[:, 1] == 1][:, 0].astype(float).tolist()

    # Оценка BPM по интервалам между битами
    if len(beat_times) > 2:
        intervals = np.diff(beat_times)
        # фильтруем слишком мелкие / большие интервалы, если хочешь
        intervals = intervals[(intervals > 0.1) & (intervals < 1.5)]
        if len(intervals) > 0:
            median_period = float(np.median(intervals))
            bpm = 60.0 / median_period
        else:
            bpm = 0.0
    else:
        bpm = 0.0

    # Ровная сетка для метронома
    metronome_grid: List[float] = []
    if bpm > 0 and beat_times:
        period = 60.0 / bpm
        first_beat = beat_times[0]
        last_time = beat_times[-1] + 4 * period

        t = first_beat
        while t < last_time:
            metronome_grid.append(t)
            t += period

    return BeatNetResult(
        bpm=bpm,
        beatTimes=beat_times,
        downbeatTimes=downbeat_times,
        metronomeGrid=metronome_grid,
    )
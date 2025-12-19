from typing import List

import essentia
import essentia.standard as es
import numpy as np


def extract_chords(audio):
    # 1. Загружаем аудио
    sample_rate = 44100

    # 2. Настройки фреймов (важно: frameSize = 2 * hopSize для ChordsDetection)
    frame_size = 4096
    hop_size = 2048

    window = es.Windowing(type="blackmanharris62")
    spectrum = es.Spectrum()

    spectral_peaks = es.SpectralPeaks(
        orderBy="magnitude",
        magnitudeThreshold=0.00001,
        minFrequency=20,
        maxFrequency=3500,
        maxPeaks=60,
    )

    hpcp = es.HPCP(
        size=36,  # можно 12, 24, 36...
        referenceFrequency=440,
        minFrequency=20,
        maxFrequency=3500,
    )

    pool = essentia.Pool()

    # 3. Генерируем HPCP-кадры
    for frame in es.FrameGenerator(
        audio,
        frameSize=frame_size,
        hopSize=hop_size,
        startFromZero=True,
        validFrameThresholdRatio=0.5,
    ):
        spec = spectrum(window(frame))
        freqs, mags = spectral_peaks(spec)  # <-- два выхода
        hpcp_vec = hpcp(freqs, mags)  # <-- два аргумента
        pool.add("tonal.hpcp", hpcp_vec)

    # 4. Детектируем аккорды по HPCP-матрице
    chords_detection = es.ChordsDetection(
        hopSize=hop_size,
        windowSize=2.0,  # окно (в секундах) для сглаживания по времени
    )

    chords, strength = chords_detection(pool["tonal.hpcp"])

    # 5. Посчитаем примерные таймкоды для каждого аккорда
    # один аккорд на кадр HPCP
    times = [i * hop_size / float(sample_rate) for i in range(len(chords))]

    # Вернем список сегментов (time, chord, strength)
    result = [
        {"timeSec": t, "chord": ch, "strength": float(st)}
        for t, ch, st in zip(times, chords, strength)
    ]

    return result

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
    chords = extract_chords(audio)

    return {
        "bpm": float(bpm),
        "beats": [float(t) for t in beats],  # таймкоды битов, с
        "key": str(key),  # например 'G'
        "scale": str(scale),  # 'major' / 'minor'
        "onsetsSec": [float(t) for t in onset_times],  # таймкоды онсетов, с
        "chords": chords,
    }
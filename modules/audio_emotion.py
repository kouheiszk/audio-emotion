#!/usr/bin/python
# -*- coding: utf-8 -*-
import atexit
import logging

import pyaudio
import time

from modules.audio_detecter import AudioDetector
from modules.audio_recorder import AudioRecorder
from modules.audio_calibrater import AudioCalibrater
from modules.sentiment_detecter import SentimentDetector

log = logging.getLogger("audio_emotion")


class AudioEmotion(object):
    CHUNK = 4096  # チャンクサイズ
    FORMAT = pyaudio.paInt16  # ビット/サンプル
    CHANNELS = 1  # チャンネル数
    RATE = 44100  # 44.1kHz
    SILENCE_LIMIT = 1
    PREV_AUDIO = 0.5

    def __init__(self):
        self.calibrater = AudioCalibrater()
        self.recorder = AudioRecorder()
        self.audio_detector = AudioDetector()
        self.sentiment_detector = SentimentDetector()
        self.sample_size = 2  # 16bits

    def analyze(self):
        self.recording = pyaudio.paContinue

        # キャリブレーション
        self.calibrater.calibrate(chunk=self.CHUNK,
                                  format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE)

        # ストリームを開く
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        output=False,
                        frames_per_buffer=self.CHUNK,
                        stream_callback=self._callback)

        # 終了条件設定
        atexit.register(p.terminate)

        # サンプルサイズを計算しなおす
        self.sample_size = p.get_sample_size(self.FORMAT)

        # ストリーム開始
        stream.start_stream()

        while stream.is_active():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.recording = pyaudio.paAbort

        # ストリーム終了/閉じる
        stream.stop_stream()
        stream.close()
        p.terminate()

    def _callback(self, data, frame_count, time_info, status):
        is_over_threshold = self.calibrater.is_over_threshold(data)
        filename = self.recorder.record(data,
                                        is_over_threshold=is_over_threshold,
                                        channels=self.CHANNELS,
                                        sample_size=self.sample_size,
                                        rate=self.RATE,
                                        buffer=self.CHUNK)

        if filename:
            phrase = self.audio_detector.transcribe_audio(filename)
            emotion = self.sentiment_detector.analyze_text(phrase)

            # TODO ディスプレイに表示
            log.debug(emotion.to_emoticon())

            self.recorder.remove(filename)

        return data, self.recording

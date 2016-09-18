#!/usr/bin/python
# -*- coding: utf-8 -*-
import atexit
import logging
import os
import wave
from collections import deque

import math
import pyaudio
import time

from modules.audio_detecter import AudioDetector
from modules.audio_calibrater import AudioCalibrater
from modules.liquid_crystal import LiquidCrystal
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
        self.audio_detector = AudioDetector()
        self.sentiment_detector = SentimentDetector()
        self.sample_size = 2  # 16bits
        self.lcd = LiquidCrystal(20, 16, 2, 3, 4, 17)

    def analyze(self):
        self.recording = pyaudio.paContinue

        # キャリブレーション
        self.calibrater.calibrate(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  chunk=self.CHUNK)

        # 初期化

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

        # 初期化
        self._initialize_frames()

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

    def _initialize_frames(self):
        rel = self.RATE / self.CHUNK
        self.started = False
        self.frames = []
        self.slid_win = deque(maxlen=math.ceil(self.SILENCE_LIMIT * rel))
        self.prev_audios = deque(maxlen=math.ceil(self.PREV_AUDIO * rel))

    def _callback(self, data, frame_count, time_info, status):
        is_over_threshold = self.calibrater.is_over_threshold(data)
        self.slid_win.append(1 if is_over_threshold else 0)

        # 閾値超えてるかどうか表示、デバッグ用
        log.debug(self.slid_win)

        if sum([x for x in self.slid_win]) > 0:
            if not self.started:
                log.debug("Start recording...")
                self.started = True
            self.frames.append(data)

        elif self.started:
            # ファイル書き出し
            filename = "data/{}.wav".format(int(time.time()))
            wf = wave.open(filename, "wb")
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.sample_size)
            wf.setframerate(self.RATE)
            wf.writeframes(b"".join(list(self.prev_audios) + self.frames))
            wf.close()
            log.debug("Finish recording, Write audio : {}".format(filename))

            # スピーチ -> テキスト
            phrase = self.audio_detector.transcribe_audio(filename)

            # テキスト -> 感情
            emotion = self.sentiment_detector.analyze_text(phrase)

            # ディスプレイに表示
            emoticon = emotion.to_emoticon()
            log.debug("Emoticon : {}".format(emoticon))

            self.lcd.clear()
            self.lcd.setCursor(0, 0)
            self.lcd.write(emoticon)

            # ファイル削除
            os.remove(filename)

            # リセット
            self._initialize_frames()

        else:
            self.prev_audios.append(data)

        return data, self.recording

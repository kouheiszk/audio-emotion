#!/usr/bin/python
# -*- coding: utf-8 -*-
import atexit

import numpy as np
import pyaudio
import time

from modules.calibrater import Calibrater
from modules.recorder import Recorder


class AudioEmotion(object):
    FORMAT = pyaudio.paInt16  # ビット/サンプル
    CHANNELS = 1  # チャンネル数
    RATE = 44100  # 44.1kHz
    FRAMES_PER_BUFFER = 4096

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.calibrater = Calibrater()
        self.recorder = Recorder()

        atexit.register(self.pa.terminate)

    def analyze(self):
        self.recording = pyaudio.paContinue

        stream = self.pa.open(format=self.FORMAT,
                              channels=self.CHANNELS,
                              rate=self.RATE,
                              input=True,
                              output=False,
                              frames_per_buffer=self.FRAMES_PER_BUFFER,
                              stream_callback=self._callback)
        stream.start_stream()

        while stream.is_active():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.recording = pyaudio.paAbort

        stream.stop_stream()
        stream.close()

        self.pa.terminate()

    def _callback(self, in_data, frame_count, time_info, status):
        data = np.fromstring(in_data, np.int16)
        average = np.average(np.abs(data))
        if not self.calibrater.finished:
            # キャリブレーションを行う
            self.calibrater.calibrate(average,
                                      rate=self.RATE,
                                      buffer=self.FRAMES_PER_BUFFER)
        else:
            # レコーディングを行う
            is_over_amplitude = self.calibrater.is_over_amplitude(average)
            filename = self.recorder.record(in_data,
                                            is_over_amplitude=is_over_amplitude,
                                            channels=self.CHANNELS,
                                            sample_size=self.pa.get_sample_size(self.FORMAT),
                                            rate=self.RATE,
                                            buffer=self.FRAMES_PER_BUFFER)

            if filename:
                print("{}".format(filename))

        return (in_data, self.recording)

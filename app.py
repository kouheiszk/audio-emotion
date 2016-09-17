#!/usr/bin/python
# -*- coding: utf-8 -*-
import atexit
import logging
import wave

import numpy as np
import pyaudio
import time

log = logging.getLogger("audio_emotion")


class Calibrater(object):
    CALIBRATION_TIME = 5  # 5sec
    THRESHOLD = 1.25  # キャリブレーション平均の25%以上の音量で反応

    def __init__(self):
        self.finished = False
        self.base = None
        self.averages = []

    def calibrate(self, average, rate, buffer):
        if not self.finished:
            needs = self.CALIBRATION_TIME * rate / buffer

            if len(self.averages) == 0:
                log.debug("Start calibration...")

            self.averages.append(average)

            if len(self.averages) >= needs:
                log.debug("Finish calibration.")
                self.finished = True
                self.base = sum(self.averages) / needs

    def is_over_amplitude(self, average):
        return average > self.base * self.THRESHOLD


class Recorder(object):
    SILENT_SPLIT_DURATION = 1  # 1sec
    MIN_AUDIO_LENGTH = 0.2  # 0.2sec以上じゃないと反応しなくする

    def __init__(self):
        self.frames = []
        self.start_time = None
        self.finish_time = None

    def record(self, samples, is_over_amplitude, channels, sample_size, rate, buffer):
        filename = None

        if is_over_amplitude:
            if self.start_time is None:
                log.debug("Start recording...")
                self.frames = []
                self.start_time = time.time()
            self.finish_time = time.time() + 1.0

        if self.start_time and self.finish_time:
            self.frames.append(samples)

        if self.finish_time and time.time() > self.finish_time:
            if time.time() > self.start_time + self.SILENT_SPLIT_DURATION + self.MIN_AUDIO_LENGTH:
                filename = "data/{}.wav".format(int(self.start_time))
                wf = wave.open(filename, "wb")
                wf.setnchannels(channels)
                wf.setsampwidth(sample_size)
                wf.setframerate(rate)
                wf.writeframes(b"".join(self.frames[0:-1 * int(self.SILENT_SPLIT_DURATION * rate / buffer)]))
                wf.close()

                log.debug("Finish recording, Write audio : {}".format(filename))
            else:
                log.debug("Too short...")

            self.frames = []
            self.start_time = None
            self.finish_time = None

        return filename


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


def main():
    # ログフォーマットの設定
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s')

    aem = AudioEmotion()
    aem.analyze()


# def main():
#     chunk = 1024
#     format = pyaudio.paInt16
#     channels = 1
#     rate = 16000
#     record_seconds = 5
#     wave_output_filename = "output.wav"
#
#     p = pyaudio.PyAudio()
#
#     stream = p.open(format=format,
#                     channels=channels,
#                     rate=rate,
#                     input=True,
#                     frames_per_buffer=chunk)
#
#     print("* recording")
#
#     frames = []
#
#     for i in range(0, int(rate / chunk * record_seconds)):
#         data = stream.read(chunk)
#         frames.append(data)
#
#     print("* done recording")
#
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
#
#     wf = wave.open(wave_output_filename, 'wb')
#     wf.setnchannels(channels)
#     wf.setsampwidth(p.get_sample_size(format))
#     wf.setframerate(rate)
#     wf.writeframes(b''.join(frames))
#     wf.close()


if __name__ == "__main__":
    main()

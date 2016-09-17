#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import time
import wave

log = logging.getLogger("audio_emotion")


class AudioRecorder(object):
    SILENT_SPLIT_DURATION = 1  # 1sec
    MIN_AUDIO_LENGTH = 0.2  # 0.2sec以上じゃないと反応しなくする

    def __init__(self):
        self.frames = []
        self.start_time = None
        self.finish_time = None

    def record(self, samples, is_over_threshold, channels, sample_size, rate, buffer):
        filename = None

        if is_over_threshold:
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
                wf.writeframes(b"".join(self.frames[0:-1 * int(self.SILENT_SPLIT_DURATION * rate / buffer / 2)]))
                wf.close()

                log.debug("Finish recording, Write audio : {}".format(filename))
            else:
                log.debug("Too short...")

            self.frames = []
            self.start_time = None
            self.finish_time = None

        return filename

    def remove(self, filename):
        os.remove(filename)

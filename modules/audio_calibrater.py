#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

import math

import audioop
import pyaudio

log = logging.getLogger("audio_emotion")


class AudioCalibrater(object):
    THRESHOLD_RATE = 1.25

    def __init__(self):
        self.threshold = 450

    def calibrate(self, format, channels, rate, chunk, num_samples=50):
        log.debug("Start calibration, Getting intensity values from mic...")

        p = pyaudio.PyAudio()
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        values = [math.sqrt(abs(audioop.avg(stream.read(chunk), 4))) for _ in range(num_samples)]
        values = sorted(values, reverse=True)
        average = sum(values[:int(num_samples * 0.5)]) / int(num_samples * 0.5)

        log.debug("Finished")
        log.debug("Average audio intensity is {}".format(average))

        stream.close()
        p.terminate()

        self.threshold = average * self.THRESHOLD_RATE

    def is_over_threshold(self, data):
        return math.sqrt(abs(audioop.avg(data, 4))) >= self.threshold

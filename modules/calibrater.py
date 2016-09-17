#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

import math

import audioop
import pyaudio

log = logging.getLogger("audio_emotion")


class Calibrater(object):
    THRESHOLD_RATE = 1.20

    def __init__(self):
        self.threshold = 450

    def calibrate(self, chunk, format, channels, rate, num_samples=50):
        log.debug("Getting intensity values from mic.")

        p = pyaudio.PyAudio()
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        values = [math.sqrt(abs(audioop.avg(stream.read(chunk), 4))) for x in range(num_samples)]
        values = sorted(values, reverse=True)
        r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)

        log.debug("Finished")
        log.debug("Average audio intensity is {}".format(r))

        stream.close()
        p.terminate()

        self.threshold = r * self.THRESHOLD_RATE

    def is_over_threshold(self, data):
        return math.sqrt(abs(audioop.avg(data, 4))) >= self.threshold

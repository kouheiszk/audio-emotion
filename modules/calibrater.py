#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

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

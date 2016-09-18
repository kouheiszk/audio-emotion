#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

import enum
import logging

log = logging.getLogger("audio_emotion")


class Emotion(enum.Enum):
    OTHER = "other"
    JOY = "joy"
    ANGER = "anger"
    SADNESS = "sadness"
    HAPPY = "happy"

    def to_emoticon(self):
        if self == Emotion.OTHER:
            return random.choice(["OTHER"])
        elif self == Emotion.JOY:
            return random.choice(["JOY"])
        elif self == Emotion.ANGER:
            return random.choice(["ANGER"])
        elif self == Emotion.SADNESS:
            return random.choice(["SADNESS"])
        elif self == Emotion.HAPPY:
            return random.choice(["HAPPY"])
        else:
            return ""

    def __str__(self):
        if self == Emotion.OTHER:
            return "その他"
        elif self == Emotion.JOY:
            return "喜"
        elif self == Emotion.ANGER:
            return "怒"
        elif self == Emotion.SADNESS:
            return "哀"
        elif self == Emotion.HAPPY:
            return "楽"
        else:
            return "ERROR"

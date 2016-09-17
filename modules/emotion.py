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
            random.choice(["(・∀・)", "(・∀・)"])
        elif self == Emotion.JOY:
            random.choice(["(*´ω｀*)", "(*´ω｀*)"])
        elif self == Emotion.ANGER:
            random.choice(["(# ﾟДﾟ)", "(# ﾟДﾟ)"])
        elif self == Emotion.SADNESS:
            random.choice(["(´；ω；｀)", "(´；ω；｀)"])
        elif self == Emotion.HAPPY:
            random.choice(["(*´∀｀*)", "(*´∀｀*)"])
        else:
            return ""

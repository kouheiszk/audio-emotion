#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from watson_developer_cloud import NaturalLanguageClassifierV1 as NaturalLanguageClassifier

from modules.config import config
from modules.emotion import Emotion

log = logging.getLogger("audio_emotion")


class SentimentDetector(object):
    def __init__(self):
        self.nlc = NaturalLanguageClassifier(username=config.natural_language_classifier["username"],
                                             password=config.natural_language_classifier["password"])

    def analyze_text(self, phrase):

        if phrase:
            response = self.nlc.classify(config.natural_language_classifier["classifier_id"], phrase)

            classes = [Emotion(klass["class_name"]) for klass in response.get("classes", [])] or [Emotion.OTHER]
            emotion = classes[0] or Emotion.OTHER
            log.debug("Detect emotion : {}".format(emotion))
        else:
            emotion = Emotion.OTHER
            log.debug("Invalid phrase.")
            
        return emotion

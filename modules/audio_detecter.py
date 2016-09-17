#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from watson_developer_cloud import SpeechToTextV1 as SpeechToText

from modules.config import config

log = logging.getLogger("audio_emotion")


class AudioDetector(object):
    def __init__(self):
        self.speech_to_text = SpeechToText(username=config.speech_to_text["username"],
                                           password=config.speech_to_text["password"])

    def transcribe_audio(self, filename):
        with open(filename, "rb") as wave_file:
            response = self.speech_to_text.recognize(wave_file,
                                                     content_type="audio/wav",
                                                     model="ja-JP_BroadbandModel")

            result = response.get("results", [{}])[0]
            alternative = result.get("alternatives", [{}])[0]
            transcript = alternative.get("transcript", "")

            return transcript.replace(" ", "")

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
        log.debug("Start transcribing audio : {}".format(filename))

        with open(filename, "rb") as wave_file:
            response = self.speech_to_text.recognize(wave_file,
                                                     content_type="audio/wav",
                                                     model="ja-JP_BroadbandModel")

            phrase = None
            results = response.get("results", [])
            if results:
                alternatives = results[0].get("alternatives", [])
                if alternatives:
                    phrase = alternatives[0].get("transcript", "").replace(" ", "")
                    log.debug("Transcribed : 「{}」".format(phrase))
            else:
                log.debug("Audio has no voice content")

            return phrase

    def transcribe_audio_by_google(self, filename):
       pass
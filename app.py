#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from modules.audio_emotion import AudioEmotion

log = logging.getLogger("audio_emotion")


def main():
    # ログフォーマットの設定
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s")

    aem = AudioEmotion()
    aem.analyze()


if __name__ == "__main__":
    main()

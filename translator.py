from googletrans import Translator
import sys


def translate(text, source_language, destination_language):
    try:
        google_translator = Translator()
        translation = google_translator.translate(text=text, src=source_language, dest=destination_language)
        return translation.text

    except:
        print('failed to translate text', file=sys.stderr)
        return text

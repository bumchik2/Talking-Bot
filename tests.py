from speech_recognizing import recognize_speech
import unittest


class SpeechRecognitionTester(unittest.TestCase):
    def general_recognize_speech_test(self, audio_path, expected_results, language, msg):
        real_result = recognize_speech(audio_path, language=language)
        real_result = real_result.lower()

        self.assertTrue(real_result in expected_results, msg=msg)

    def recognize_speech_english_test(self):
        audio_path = 'Audio/english.wav'
        expected_result = ('123', '1 2 3', 'one two three')
        msg = ' English speech recognition test failed'

        self.general_recognize_speech_test(audio_path, expected_result, 'en-US', msg)

    def recognize_speech_russian_test(self):
        audio_path = 'Audio/russian.wav'
        expected_results = ('привет', )
        msg = ' Russian speech recognition test failed'

        self.general_recognize_speech_test(audio_path, expected_results, 'ru-RU', msg)


def test_all():
    srt = SpeechRecognitionTester()
    srt.recognize_speech_english_test()
    srt.recognize_speech_russian_test()


if __name__ == '__main__':
    test_all()

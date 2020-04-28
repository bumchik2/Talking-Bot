import speech_recognition as sr


def recognize_speech(file_path, language):
    r = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    try:
        result = r.recognize_google(audio, language=language)
        return result
    except (sr.UnknownValueError, sr.RequestError):
        return ''

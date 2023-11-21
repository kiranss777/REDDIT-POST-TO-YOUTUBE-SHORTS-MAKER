
import pyttsx3

voiceoverDir = "Voiceovers"

def create_voice_over(fileName, text):
    filePath = f"{voiceoverDir}/{fileName}.mp3"
    engine = pyttsx3.init()
    zira_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
    engine.setProperty('voice', zira_voice_id)
    engine.save_to_file(text, filePath)
    engine.runAndWait()
    return filePath
"""
from gtts import gTTS
import os

voiceoverDir = "Voiceovers"

def create_voice_over(fileName, text):
    filePath = f"{voiceoverDir}/{fileName}.mp3"
    
    tts = gTTS(text=text, lang='en')  # Create gTTS object
    tts.save(filePath)  # Save the generated audio file
    
    return filePath
"""
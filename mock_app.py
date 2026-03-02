import os
import json
import pyttsx3
from gtts import gTTS
from playsound import playsound
from langdetect import detect
import time

class MoroVoiceAssistant:
    def __init__(self, assets_dir="audio_assets", config_file="voice_config.json"):
        self.assets_dir = assets_dir
        self.config_file = config_file
        self.phrases = {}
        
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)
            
        self.load_config()
        
        # Initialize offline TTS engine
        self.offline_engine = pyttsx3.init()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.phrases = json.load(f)
        else:
            self.phrases = {
                "MODEL_1": {},
                "MODEL_2": {},
                "MODEL_3": {},
                "MODEL_4": {}
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.phrases, f, indent=4, ensure_ascii=False)

    def generate_audio(self, model_id, event_type, text, lang=None, mode="online"):
        if lang is None:
            try:
                lang = detect(text)
            except:
                lang = 'en'
        
        filename = f"{model_id}_{event_type}_{lang}.mp3"
        filepath = os.path.join(self.assets_dir, filename)
        
        if mode == "online":
            try:
                tts = gTTS(text=text, lang=lang)
                tts.save(filepath)
                print(f"[ONLINE] Generated audio: {filepath}")
            except Exception as e:
                print(f"Online TTS failed, falling back to offline: {e}")
                self.generate_offline(text, filepath)
        else:
            self.generate_offline(text, filepath)
            
        return filepath, lang

    def generate_offline(self, text, filepath):
        # Note: pyttsx3 usually saves to wav, but we'll try to keep consistency if possible
        # For simplicity in this CLI version, we'll use pyttsx3 to speak directly if needed,
        # but here we attempt to save.
        self.offline_engine.save_to_file(text, filepath)
        self.offline_engine.runAndWait()
        print(f"[OFFLINE] Generated audio: {filepath}")

    def add_and_store(self, model_id, event_type, text, lang=None):
        filepath, detected_lang = self.generate_audio(model_id, event_type, text, lang)
        
        if model_id not in self.phrases:
            self.phrases[model_id] = {}
            
        self.phrases[model_id][event_type] = {
            "text": text,
            "lang": detected_lang,
            "filepath": filepath
        }
        self.save_config()
        return filepath

    def preview_audio(self, filepath):
        if not os.path.exists(filepath):
            print(f"Error: File {filepath} not found.")
            return
            
        print(f"Playing preview: {filepath}")
        try:
            playsound(filepath)
        except Exception as e:
            print(f"Playback error: {e}")

    def speak(self, model_id, event_type):
        if model_id in self.phrases and event_type in self.phrases[model_id]:
            phrase_data = self.phrases[model_id][event_type]
            filepath = phrase_data['filepath']
            
            if os.path.exists(filepath):
                print(f"[Moro-AI Alert] Model: {model_id}, Event: {event_type}")
                try:
                    playsound(filepath)
                except Exception as e:
                    print(f"Playback error: {e}")
            else:
                print(f"Error: Audio file {filepath} missing. Generating now...")
                self.generate_audio(model_id, event_type, phrase_data['text'], phrase_data['lang'])
                try:
                    playsound(filepath)
                except Exception as e:
                    print(f"Playback error: {e}")
        else:
            print(f"No audio registered for {model_id} - {event_type}")

if __name__ == "__main__":
    # Quick Test
    assistant = MoroVoiceAssistant()
    # assistant.add_and_store("MODEL_2", "TIGER_DETECTED", "Tiger detected outside, stay safe", "en")
    # assistant.speak("MODEL_2", "TIGER_DETECTED")

from google import genai
import os
import pygame
import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = os.getenv("newsapi")


def speak_old(text):
    engine.say(text)
    engine.runAndWait()


def speak(text):
    tts = gTTS(text)
    tts.save("temp.mp3")

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load("temp.mp3")

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove("temp.mp3")


def aiProcess(command):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    Reply in 2–3 short lines.
    No emojis.
    No bullet points.
    No extra details.

    Question: {command}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


def processCommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)

    elif "news" in c.lower():
        r = requests.get(
            f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}"
        )
        if r.status_code == 200:
            # Parse the JSON response
            data = r.json()

            # Extract the articles
            articles = data.get("articles", [])

            # Print the headlines
            for article in articles:
                speak(article["title"])

    else:
        # Let OpenAI handle the request
        output = aiProcess(c)
        speak(output)


if __name__ == "__main__":
    speak("Initializing Jarvis...")
print("Jarvis initialized.")
print("Say 'Jarvis' to activate.\n")

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.8  # pause before phrase considered complete
recognizer.energy_threshold = 300  # mic sensitivity (auto-adjusts later)

while True:
    try:
        # ---- WAKE WORD LISTENING ----
        print("\n[WAITING] Say 'Jarvis'...")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=5,  # time to START speaking
                phrase_time_limit=3,  # time to FINISH speaking
            )

        wake_word = recognizer.recognize_google(audio)
        print(f"[DETECTED] You said: {wake_word}")

        if wake_word.lower() == "jarvis":
            speak("Yes?")
            print("\n[JARVIS ACTIVE] Listening for command...")

            # ---- COMMAND LISTENING ----
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source,
                    timeout=8,  # more time to think
                    phrase_time_limit=6,  # more time to speak
                )

            command = recognizer.recognize_google(audio)
            print(f"[COMMAND] {command}")

            processCommand(command)

    except sr.WaitTimeoutError:
        print("[TIMEOUT] No speech detected.")
        continue

    except sr.UnknownValueError:
        print("[ERROR] Could not understand audio.")
        continue

    except sr.RequestError as e:
        print(f"[ERROR] Speech service error: {e}")
        continue

    except Exception as e:
        print(f"[FATAL ERROR] {e}")

import speech_recognition as sr
import serial
import time
import requests

# ----- Serial connection to Arduino -----
arduino = serial.Serial('COM3', 9600)   # ⚠ apna COM port check kar lo 
time.sleep(2)

# ----- ThingSpeak setup -----
API_KEY = "53MI3ITDBSR24YTW"

def send_to_thingspeak(word_count, total_time):
    try:
        url = f"https://api.thingspeak.com/update?api_key={API_KEY}&field1={word_count}&field2={total_time}"
        requests.get(url)
    except:
        print("⚠ ThingSpeak update failed!")

recognizer = sr.Recognizer()
mic = sr.Microphone()

print("\n🎧 Voice listening started... say 'stop' to end.\n")

start_time = time.time()
word_count = 0

while True:
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("Listening...")
            # ⚙ phrase_time_limit removed for continuous chunks
            audio = recognizer.listen(source,timeout=None,phrase_time_limit=None)

        # ✅ Force English output
        text = recognizer.recognize_google(audio, language='en-IN')
        text = text.lower()
        print(f"🗣 You said: {text}")

        if "stop" in text:
            print("🛑 Stopped by user.")
            break

        words = text.split()
        word_count += len(words)
        total_time = round(time.time() - start_time)

        # Send word/time to Arduino
        data = f"{word_count},{total_time}\n"
        arduino.write(data.encode())

        # Send to ThingSpeak
        send_to_thingspeak(word_count, total_time)

        print(f"✅ Words: {word_count} | Time: {total_time} sec\n")

        # 🔔 Trigger buzzer from Python side when words exceed 20
        if word_count >= 10:
            arduino.write(b"BUZZ\n")

    except sr.UnknownValueError:
        print("⚠ Didn't catch that.")
    except Exception as e:
        print("Error:", e)

arduino.close()
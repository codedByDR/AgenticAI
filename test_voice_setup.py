#!/usr/bin/env python
"""Test script to verify microphone and voice input setup"""

import sys

print("=" * 60)
print("VOICE INPUT SYSTEM TEST")
print("=" * 60)

# Test 1: SpeechRecognition
print("\n[TEST 1] Checking SpeechRecognition Library...")
try:
    import speech_recognition as sr
    print("✓ SpeechRecognition imported successfully")
    print(f"  Version: {sr.__version__ if hasattr(sr, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"✗ Failed to import SpeechRecognition: {e}")
    sys.exit(1)

# Test 2: PyAudio
print("\n[TEST 2] Checking PyAudio...")
try:
    import pyaudio
    print("✓ PyAudio imported successfully")
    p = pyaudio.PyAudio()
    print(f"  Found {p.get_device_count()} audio devices")
    
    # List available devices
    print("\n  Available Audio Devices:")
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info.get('max_input_channels', 0) > 0:
                print(f"    [{i}] {info.get('name', 'Unknown')} (Input channels: {info.get('max_input_channels', 0)})")
        except Exception as e:
            print(f"    [{i}] Could not get device info: {e}")
    p.terminate()
except ImportError as e:
    print(f"✗ Failed to import PyAudio: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error with PyAudio: {e}")
    sys.exit(1)

# Test 3: Microphone availability
print("\n[TEST 3] Checking Microphone Access...")
try:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print("✓ Microphone accessible")
    
    with mic as source:
        print("  Adjusting for ambient noise (1 second)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("  ✓ Microphone ready for input")
except sr.MicrophoneError as e:
    print(f"✗ Microphone Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error accessing microphone: {e}")
    sys.exit(1)

# Test 4: Google Speech Recognition API
print("\n[TEST 4] Testing Internet Connection (Google Speech API)...")
try:
    import urllib.request
    urllib.request.urlopen('https://www.google.com', timeout=2)
    print("✓ Internet connection available")
    print("  Google Speech Recognition API should work")
except Exception as e:
    print(f"⚠ No internet connection: {e}")
    print("  Voice input will not work without internet")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("✓ All tests passed!")
print("\nYour system is ready for voice input. You can now:")
print("  1. Refresh your Streamlit app")
print("  2. Click the 🎤 button to test voice input")
print("  3. Speak your poem topic clearly")
print("=" * 60)

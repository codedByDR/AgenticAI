#!/usr/bin/env python
"""Microphone audio capture test - diagnose audio input issues"""

import speech_recognition as sr
import sys

print("=" * 70)
print("MICROPHONE AUDIO CAPTURE TEST")
print("=" * 70)

# Step 1: List available microphones
print("\n[STEP 1] Available Microphone Devices:")
print("-" * 70)

try:
    # Try to get device names from pyaudio
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        print("Available Devices:")
        default_input = p.get_default_input_device_info()
        print(f"\nDefault Input Device:")
        print(f"  [{default_input.get('index', '?')}] {default_input.get('name', 'Unknown')}")
        print(f"  Input Channels: {default_input.get('max_input_channels', 0)}")
        print(f"  Sample Rate: {default_input.get('default_sample_rate', 'Unknown')} Hz")
        
        print(f"\nAll Devices with Input:")
        for i in range(p.get_device_count()):
            try:
                info = p.get_device_info_by_index(i)
                input_ch = info.get('max_input_channels', 0)
                if input_ch > 0:
                    print(f"  [{i}] {info.get('name', 'Unknown')} ({input_ch} channels)")
            except:
                pass
        p.terminate()
    except Exception as e:
        print(f"  Could not get device details: {e}")
        
except Exception as e:
    print(f"✗ Error listing microphones: {e}")
    sys.exit(1)

# Step 2: Test default microphone
print("\n[STEP 2] Testing Default Microphone...")
print("-" * 70)

try:
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("✓ Microphone object created")
    print("  Listening for 5 seconds...")
    print("  Please speak something now!\n")
    
    with microphone as source:
        # Adjust for ambient noise
        print("  → Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("  ✓ Noise adjustment complete")
        
        # Try to listen
        print("  → Listening for speech (5 seconds)...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print(f"  ✓ Audio captured! ({len(audio.frame_data)} bytes)")
            
            # Try to recognize
            print("  → Sending to Google Speech Recognition...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"  ✓ Recognized: '{text}'")
                print("\n" + "=" * 70)
                print("SUCCESS! Your microphone is working perfectly!")
                print("=" * 70)
            except sr.UnknownValueError:
                print("  ⚠ Audio captured but could not be understood")
                print("  → Try speaking more clearly or loudly")
            except sr.RequestError as e:
                print(f"  ✗ Google Speech API error: {e}")
                print("  → Check your internet connection")
                
        except sr.WaitTimeoutError:
            print("  ✗ Timeout - No audio detected!")
            print("\n  TROUBLESHOOTING:")
            print("  1. Check if microphone is connected")
            print("  2. Check if microphone is muted (hardware or software)")
            print("  3. Try speaking LOUDER")
            print("  4. Check volume levels in Windows Sound Settings")
            print("  5. Try a different microphone device")
            sys.exit(1)
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)

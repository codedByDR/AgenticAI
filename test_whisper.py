#!/usr/bin/env python
"""Test Whisper speech recognition - MUCH BETTER than Google API!"""

import speech_recognition as sr
import whisper
import tempfile
import os

print("=" * 70)
print("WHISPER SPEECH RECOGNITION TEST")
print("=" * 70)

print("\n✓ Whisper is installed - this is MUCH more accurate than Google!")
print("  Whisper handles:")
print("  • Accents and different pronunciations")
print("  • Background noise")
print("  • Unclear or mumbled speech")
print("  • Multiple languages")

print("\n[STEP 1] Loading Whisper Model...")
print("-" * 70)
try:
    print("Loading 'base' model (medium accuracy, fast)...")
    model = whisper.load_model("base")
    print("✓ Model loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    exit(1)

print("\n[STEP 2] Recording Audio from Microphone...")
print("-" * 70)
print("LISTENING FOR 8 SECONDS - SPEAK NOW!")
print("Please say a clear phrase or word (e.g., 'Morning', 'Love', 'Nature')\n")

try:
    recognizer = sr.Recognizer()
    
    # Optimize settings
    recognizer.energy_threshold = 4000
    recognizer.dynamic_energy_threshold = True
    recognizer.phrase_threshold = 0.3
    
    with sr.Microphone() as source:
        # Adjust for noise
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✓ Ready - listening for 8 seconds...\n")
        
        # Capture audio
        audio = recognizer.listen(source, timeout=8, phrase_time_limit=8)
        print(f"✓ Audio captured ({len(audio.frame_data)} bytes)\n")
        
except Exception as e:
    print(f"✗ Microphone error: {e}")
    exit(1)

print("[STEP 3] Transcribing with Whisper...")
print("-" * 70)

try:
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio.get_wav_data())
        tmp_path = tmp.name
    
    print("Processing audio with Whisper...")
    
    # Transcribe
    result = model.transcribe(tmp_path, language="en", verbose=False)
    text = result["text"].strip()
    confidence = result.get("confidence", "N/A")
    
    # Clean up
    os.remove(tmp_path)
    
    if text:
        print(f"\n✓ SUCCESS!")
        print(f"  Recognized: '{text}'")
        print(f"  Language: {result.get('language', 'English')}")
        print("\n" + "=" * 70)
        print("Whisper is now active in your PoemAgent!")
        print("=" * 70)
    else:
        print("⚠ No text recognized - try speaking louder or clearer")
        
except Exception as e:
    print(f"✗ Whisper error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

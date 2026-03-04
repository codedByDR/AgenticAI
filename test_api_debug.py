#!/usr/bin/env python
"""Test script to debug the poem generation API"""

import requests
import json
import time

# Wait a bit for backend to be ready
time.sleep(2)

BASE_URL = "http://localhost:8000"

# Test 1: Health check
print("=" * 50)
print("TEST 1: Health Check")
print("=" * 50)
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\n")

# Test 2: Root endpoint
print("=" * 50)
print("TEST 2: Root Endpoint")
print("=" * 50)
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\n")

# Test 3: Generate poem (English only to start)
print("=" * 50)
print("TEST 3: Generate English Poem")
print("=" * 50)
try:
    payload = {
        "topic": "Morning",
        "language": "english",
        "style": "free verse",
        "mood": "peaceful"
    }
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/generate-poem",
        json=payload,
        timeout=30
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"English Poem:\n{result.get('english_poem', 'N/A')[:200]}...")
        print(f"Audio Generated: {'Yes' if result.get('english_audio') else 'No'}")
    else:
        print(f"Error Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)

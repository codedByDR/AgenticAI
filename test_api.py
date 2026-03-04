#!/usr/bin/env python
"""Test API key and generate poem"""

from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()

# Check API key
api_key = os.environ.get("OPENAI_API_KEY")
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key starts with: {api_key[:20]}...")

try:
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Test API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poet."},
            {"role": "user", "content": "Write a short poem about nature."}
        ],
        max_tokens=100
    )
    
    print("✅ OpenAI API is working!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

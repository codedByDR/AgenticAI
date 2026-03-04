"""
FastAPI Backend for Poem Generator AI Agent
Handles Groq API integration and poem generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from typing import Optional
import base64
from gtts import gTTS
import io
from dotenv import load_dotenv
import logging
import traceback

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Groq API Key - load from environment variable
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY environment variable is not set")
    raise ValueError("GROQ_API_KEY environment variable is not set")

logger.info(f"Groq API Key loaded: {GROQ_API_KEY[:10]}...")

app = FastAPI(title="Poem Generator API", description="AI-powered poem generator in Tamil and English using Groq")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


class PoemRequest(BaseModel):
    topic: str
    language: str = "both"  # "tamil", "english", or "both"
    style: Optional[str] = "free verse"
    mood: Optional[str] = "neutral"


class PoemResponse(BaseModel):
    tamil_poem: Optional[str] = None
    english_poem: Optional[str] = None
    tamil_audio: Optional[str] = None
    english_audio: Optional[str] = None


def generate_poem_with_groq(topic: str, language: str, style: str, mood: str) -> str:
    """Generate poem using Groq API"""
    
    try:
        language_prompt = {
            "tamil": "Write a beautiful poem in Tamil (தமிழ்)",
            "english": "Write a beautiful poem in English",
            "both": "Write beautiful poems in both Tamil (தமிழ்) and English"
        }
        
        prompt = f"""You are a creative poet. {language_prompt.get(language, 'Write a beautiful poem')}.
        
Topic: {topic}
Style: {style}
Mood: {mood}

Please create an original, creative poem about this topic. Make it emotionally evocative and memorable. Write ONLY the poem without any additional text or explanations.
"""
        
        logger.info(f"Generating {language} poem for topic: {topic}")
        logger.info(f"Using Groq model: llama-3.1-8b-instant")
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a talented poet who writes beautiful, emotional poems in both Tamil and English. You create unique, creative, and emotionally evocative poems."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.8
        )
        
        poem_content = response.choices[0].message.content
        logger.info(f"Successfully generated {language} poem")
        return poem_content
        
    except Exception as e:
        error_msg = f"Error generating poem: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


def text_to_speech(text: str, language: str) -> str:
    """Convert text to speech and return base64 encoded audio"""
    try:
        logger.info(f"Generating {language} audio for {len(text)} characters")
        # Map language to gTTS lang code
        lang_code = "ta" if language == "tamil" else "en"
        
        # Generate speech
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # Convert to base64
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode('utf-8')
        logger.info(f"Successfully generated {language} audio")
        
        return f"data:audio/mp3;base64,{audio_base64}"
    except Exception as e:
        error_msg = f"Error generating speech: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return None


@app.post("/generate-poem", response_model=PoemResponse)
async def generate_poem(request: PoemRequest):
    """Generate poem in Tamil, English, or both"""
    
    try:
        logger.info(f"Received poem request: topic={request.topic}, language={request.language}, style={request.style}, mood={request.mood}")
        
        result = PoemResponse()
        
        # Generate Tamil poem
        if request.language in ["tamil", "both"]:
            logger.info("Generating Tamil poem...")
            tamil_poem = generate_poem_with_groq(request.topic, "tamil", request.style, request.mood)
            result.tamil_poem = tamil_poem
            
            # Generate Tamil audio
            logger.info("Generating Tamil audio...")
            result.tamil_audio = text_to_speech(tamil_poem, "tamil")
        
        # Generate English poem
        if request.language in ["english", "both"]:
            logger.info("Generating English poem...")
            english_poem = generate_poem_with_groq(request.topic, "english", request.style, request.mood)
            result.english_poem = english_poem
            
            # Generate English audio
            logger.info("Generating English audio...")
            result.english_audio = text_to_speech(english_poem, "english")
        
        logger.info("Successfully generated all poems and audio")
        return result
        
    except Exception as e:
        error_msg = f"Error in generate_poem endpoint: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/")
async def root():
    return {"message": "Poem Generator API is running!", "status": "active"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

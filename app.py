"""
Streamlit Frontend for Poem Generator AI Agent
Beautiful UI with voice input and output capabilities
"""

import streamlit as st
import requests
import logging
import tempfile
import os

# Setup logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and test speech recognition
SPEECH_RECOGNITION_AVAILABLE = False
PYAUDIO_AVAILABLE = False
WHISPER_AVAILABLE = False
sr = None

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    logger.info("✓ SpeechRecognition library loaded successfully")
    
    # Test if PyAudio/microphone is available
    try:
        import pyaudio
        PYAUDIO_AVAILABLE = True
        logger.info("✓ PyAudio available")
    except ImportError:
        logger.warning("⚠ PyAudio not available - microphone may not work")
        PYAUDIO_AVAILABLE = False
        
except ImportError as e:
    logger.error(f"✗ SpeechRecognition not installed: {e}")
    sr = None
    SPEECH_RECOGNITION_AVAILABLE = False

# Try to import Whisper for better speech recognition
try:
    import whisper
    WHISPER_AVAILABLE = True
    logger.info("✓ OpenAI Whisper available - will use for speech recognition")
except ImportError:
    logger.warning("⚠ Whisper not available - will fall back to Google Speech API")
    WHISPER_AVAILABLE = False
from gtts import gTTS
import io
import base64
import time
from dataclasses import dataclass
from typing import Optional, Tuple
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="Poem Generator AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px #fff, 0 0 20px #ff6b6b; }
        to { text-shadow: 0 0 20px #fff, 0 0 30px #48dbfb; }
    }
    
    /* Card styling */
    .poem-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .poem-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.4);
        transition: all 0.3s ease;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
    }
    
    /* Voice button styling */
    .voice-btn {
        background: linear-gradient(45deg, #48dbfb, #0abde3) !important;
        box-shadow: 0 4px 15px rgba(72, 219, 251, 0.4) !important;
    }
    
    .voice-btn:hover {
        box-shadow: 0 6px 20px rgba(72, 219, 251, 0.6) !important;
    }
    
    .voice-btn.recording {
        background: linear-gradient(45deg, #ff6b6b, #ee5253) !important;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 0.8rem 1rem;
        color: white;
        font-size: 1.1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #48dbfb;
        box-shadow: 0 0 10px rgba(72, 219, 251, 0.3);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
    }
    
    /* Language badges */
    .lang-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.2rem;
        margin: 0.5rem;
    }
    
    .tamil-badge {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
    }
    
    .english-badge {
        background: linear-gradient(45deg, #48dbfb, #0abde3);
    }
    
    /* Audio player styling */
    .audio-player {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Loading spinner */
    .loading-text {
        font-size: 1.2rem;
        color: #48dbfb;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# Session state for managing state
if 'poem_result' not in st.session_state:
    st.session_state.poem_result = None
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'recognized_text' not in st.session_state:
    st.session_state.recognized_text = ""


@dataclass
class PoemResult:
    tamil_poem: Optional[str] = None
    english_poem: Optional[str] = None
    tamil_audio: Optional[str] = None
    english_audio: Optional[str] = None


def recognize_speech() -> Tuple[bool, str]:
    """Recognize speech using Whisper or Google, whichever is available"""
    
    if not SPEECH_RECOGNITION_AVAILABLE:
        return False, "Speech recognition library not installed. Install with: pip install SpeechRecognition"
    
    if not PYAUDIO_AVAILABLE:
        return False, "PyAudio not available. Please install with: pip install pyaudio"
    
    try:
        logger.info("Attempting to access microphone...")
        
        # Use default microphone
        mic = sr.Microphone()
        recognizer = sr.Recognizer()
        
        # Optimize recognizer settings
        recognizer.energy_threshold = 4000
        recognizer.dynamic_energy_threshold = True
        recognizer.phrase_threshold = 0.3
        
        with mic as source:
            logger.info("Microphone accessed - adjusting for ambient noise...")
            
            # Longer noise adjustment for accuracy
            recognizer.adjust_for_ambient_noise(source, duration=3)
            
            logger.info("Listening for speech (up to 15 seconds)...")
            # Capture audio
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=15)
            logger.info(f"Audio captured: {len(audio.frame_data)} bytes")
            
            # Try Whisper first if available (much more accurate)
            if WHISPER_AVAILABLE:
                try:
                    logger.info("Using OpenAI Whisper for speech recognition...")
                    
                    # Save audio to temporary file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        tmp.write(audio.get_wav_data())
                        tmp_path = tmp.name
                    
                    try:
                        # Load Whisper model (tiny model is fast, but base is more accurate)
                        model = whisper.load_model("base")
                        logger.info("Whisper model loaded")
                        
                        # Transcribe
                        result = model.transcribe(tmp_path, language="en", verbose=False)
                        text = result["text"].strip()
                        
                        if text:
                            logger.info(f"Whisper recognized: '{text}'")
                            return True, text
                        else:
                            logger.warning("Whisper: No text recognized")
                            
                    finally:
                        # Clean up temp file
                        try:
                            os.remove(tmp_path)
                        except:
                            pass
                            
                except Exception as e:
                    logger.warning(f"Whisper error: {e} - will try Google API")
            
            # Fallback to Google Speech Recognition
            try:
                logger.info("Using Google Speech Recognition API...")
                text = recognizer.recognize_google(audio, language='en-US')
                logger.info(f"Google recognized: '{text}'")
                return True, text
                
            except sr.UnknownValueError:
                logger.warning("Google: Could not understand the audio")
                return False, "Could not understand your speech clearly. Please try again in a quieter location."
                
            except sr.RequestError as e:
                logger.warning(f"Google API error: {e}")
                return False, f"Google API Error: {e}. Check internet connection."
                
    except sr.MicrophoneError as e:
        logger.error(f"Microphone error: {e}")
        return False, f"Microphone Error: Make sure it's connected and not in use by another app."
        
    except sr.WaitTimeoutError:
        logger.warning("No speech detected (timeout)")
        return False, "No speech detected. Please speak clearly and loudly."
        
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, f"Error: {str(e)}"


def play_audio(audio_base64: str):
    """Play audio from base64 string"""
    if audio_base64:
        st.audio(audio_base64, format='audio/mp3')


def create_audio_download(audio_base64: str, filename: str):
    """Create audio download link"""
    if audio_base64:
        audio_bytes = base64.b64decode(audio_base64.split(',')[1])
        st.download_button(
            label=f"⬇️ Download {filename} Audio",
            data=audio_bytes,
            file_name=f"{filename}.mp3",
            mime="audio/mp3"
        )


def call_api(topic: str, language: str, style: str, mood: str) -> PoemResult:
    """Call the FastAPI backend"""
    try:
        response = requests.post(
            "http://localhost:8000/generate-poem",
            json={
                "topic": topic,
                "language": language,
                "style": style,
                "mood": mood
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return PoemResult(
                tamil_poem=data.get("tamil_poem"),
                english_poem=data.get("english_poem"),
                tamil_audio=data.get("tamil_audio"),
                english_audio=data.get("english_audio")
            )
        else:
            st.error(f"API Error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to API. Make sure the backend is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def main():
    # Header
    st.markdown('<h1 class="main-header">📝 AI Poem Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #a0a0a0;">Create beautiful poems in Tamil and English with Voice AI</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show voice input capabilities
    if SPEECH_RECOGNITION_AVAILABLE and PYAUDIO_AVAILABLE:
        capabilities_col1, capabilities_col2, capabilities_col3 = st.columns(3)
        with capabilities_col1:
            st.success("✓ Microphone Ready")
        with capabilities_col2:
            if WHISPER_AVAILABLE:
                st.success("✓ Using Whisper AI (Accurate!)")
            else:
                st.info("ℹ Using Google Speech API")
        with capabilities_col3:
            st.info("💡 Speak clearly into microphone")
    elif not SPEECH_RECOGNITION_AVAILABLE or not PYAUDIO_AVAILABLE:
        with st.expander("ℹ️ Voice Input Status"):
            col1, col2, col3 = st.columns(3)
            with col1:
                if SPEECH_RECOGNITION_AVAILABLE:
                    st.success("✓ SpeechRecognition installed")
                else:
                    st.error("✗ SpeechRecognition not installed")
                    st.code("pip install SpeechRecognition")
            with col2:
                if PYAUDIO_AVAILABLE:
                    st.success("✓ PyAudio available")
                else:
                    st.error("✗ PyAudio not available")
                    st.code("pip install pyaudio")
            with col3:
                if WHISPER_AVAILABLE:
                    st.success("✓ Whisper available")
                else:
                    st.info("Whisper not available")
                st.info("💡 You can still use text input to create poems")
    
    # Create two columns for input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Topic input with voice input
        st.markdown("### 🎯 Topic")
        
        # Voice input button
        voice_col1, voice_col2 = st.columns([5, 1])
        
        with voice_col1:
            topic = st.text_input(
                "Enter your poem topic:",
                placeholder="e.g., Love, Nature, Life, Friendship...",
                key="topic_input",
                value=st.session_state.recognized_text
            )
        
        with voice_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if SPEECH_RECOGNITION_AVAILABLE and PYAUDIO_AVAILABLE:
                if st.button("🎤", key="voice_input", help="Click to speak", use_container_width=True):
                    spinner_msg = "🎤 Listening... Speak now!" if WHISPER_AVAILABLE else "🎤 Listening (Google API)..."
                    with st.spinner(spinner_msg):
                        success, text = recognize_speech()
                        if success:
                            st.session_state.recognized_text = text
                            st.rerun()
                        else:
                            st.error(f"❌ {text}")
            else:
                disabled_msg = []
                if not SPEECH_RECOGNITION_AVAILABLE:
                    disabled_msg.append("SpeechRecognition not installed")
                if not PYAUDIO_AVAILABLE:
                    disabled_msg.append("PyAudio not available")
                
                st.button(
                    "🎤",
                    key="voice_input",
                    help=f"Not available: {', '.join(disabled_msg)}",
                    disabled=True,
                    use_container_width=True
                )
    
    with col2:
        # Language selection
        st.markdown("### 🌐 Language")
        language = st.selectbox(
            "Select language:",
            ["both", "tamil", "english"],
            format_func=lambda x: {
                "both": "🌏 Both (Tamil & English)",
                "tamil": "🇮🇳 Tamil (தமிழ்)",
                "english": "🇬🇧 English"
            }[x]
        )
    
    # Style and Mood in columns
    st.markdown("### ✨ Style & Mood")
    style_col, mood_col = st.columns(2)
    
    with style_col:
        style = st.selectbox(
            "Poem Style:",
            ["free verse", "haiku", "sonnet", "limerick", "acrostic", "ballad"],
            format_func=lambda x: x.title()
        )
    
    with mood_col:
        mood = st.selectbox(
            "Mood:",
            ["neutral", "happy", "sad", "romantic", "inspirational", "mysterious", "peaceful"]
        )
    
    st.markdown("---")
    
    # Generate button
    if st.button("🚀 Generate Poem", type="primary"):
        if not topic:
            st.warning("Please enter a topic for your poem!")
        else:
            with st.spinner("✨ Creating your poem... This may take a moment..."):
                st.session_state.poem_result = call_api(topic, language, style, mood)
    
    # Display results
    if st.session_state.poem_result:
        result = st.session_state.poem_result
        
        st.markdown("---")
        st.markdown("## 📜 Your Poems")
        
        # Tamil poem
        if result.tamil_poem:
            st.markdown(f"""
            <div class="poem-card">
                <h2 style="color: #feca57;">🇮🇳 Tamil Poem (தமிழ்)</h2>
                <hr>
                <p style="font-size: 1.3rem; line-height: 1.8; white-space: pre-wrap;">{result.tamil_poem}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tamil audio
            if result.tamil_audio:
                st.markdown("#### 🔊 Tamil Audio")
                play_audio(result.tamil_audio)
                create_audio_download(result.tamil_audio, "tamil_poem")
        
        # English poem
        if result.english_poem:
            st.markdown(f"""
            <div class="poem-card">
                <h2 style="color: #48dbfb;">🇬🇧 English Poem</h2>
                <hr>
                <p style="font-size: 1.3rem; line-height: 1.8; white-space: pre-wrap;">{result.english_poem}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # English audio
            if result.english_audio:
                st.markdown("#### 🔊 English Audio")
                play_audio(result.english_audio)
                create_audio_download(result.english_audio, "english_poem")
        
        # Success message
        st.success("🎉 Your poem has been generated successfully!")
        
        # New poem button
        if st.button("🔄 Create Another Poem"):
            st.session_state.poem_result = None
            st.session_state.recognized_text = ""
            st.rerun()
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("## ℹ️ About")
        st.markdown("""
        ### AI Poem Generator
        
        Create beautiful poems in **Tamil** and **English** using artificial intelligence.
        
        **Features:**
        - 🌐 Bilingual support (Tamil & English)
        - 🎤 Voice input
        - 🔊 Text-to-speech audio output
        - ✨ Multiple styles and moods
        - 📱 Beautiful modern UI
        """)
        
        st.markdown("---")
        st.markdown("### 🎨 Poem Styles")
        st.markdown("""
        - **Free Verse**: No structure constraints
        - **Haiku**: 5-7-5 syllable pattern
        - **Sonnet**: 14-line poetic form
        - **Limerick**: 5-line humorous poem
        - **Acrostic**: First letters spell a word
        - **Ballad**: Narrative poem
        """)
        
        st.markdown("---")
        st.markdown("### 🚀 How to Use")
        st.markdown("""
        1. Enter a topic or speak it
        2. Choose language preference
        3. Select style and mood
        4. Click Generate
        5. Listen to audio output
        """)
        
        # API status check
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                st.markdown("---")
                st.markdown("✅ **API Status: Online**")
        except:
            st.markdown("---")
            st.markdown("⚠️ **API Status: Offline**")
            st.markdown("Run: `python main.py`")


if __name__ == "__main__":
    main()

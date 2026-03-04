# AI Poem Generator - Tamil & English

A beautiful AI-powered poem generator with FastAPI backend and Streamlit frontend. Generate poems in Tamil and English with voice input and output capabilities.

## 🌟 Features

- **Bilingual Support**: Create poems in Tamil (தமிழ்) and English
- **Voice Input**: Speak your poem topic using microphone
- **Voice Output**: Listen to generated poems with text-to-speech
- **Beautiful UI**: Modern, responsive design with animations
- **Multiple Styles**: Free verse, Haiku, Sonnet, Limerick, Acrostic, Ballad
- **Mood Selection**: Happy, Sad, Romantic, Inspirational, Mysterious, Peaceful

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Microphone for voice input
- Internet connection (for OpenAI API and gTTS)

### Installation

1. **Clone the repository**
   ```bash
   cd your-project-folder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   For Windows, you may also need:
   ```bash
   pip install pyaudio
   ```
   
   If pyaudio fails to install, try:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

3. **Configure API Key**

   Create a `.env` file in the project root with your OpenAI API key:
   ```bash
   echo OPENAI_API_KEY=your_api_key_here > .env
   ```

### Running the Application

1. **Start the FastAPI Backend** (Terminal 1)
   ```bash
   python main.py
   ```
   The API will run at `http://localhost:8000`

2. **Start the Streamlit Frontend** (Terminal 2)
   ```bash
   streamlit run app.py
   ```

3. **Open your browser**
   Navigate to `http://localhost:8501`

## 📖 Usage

1. **Enter a Topic**: Type your poem topic or click the 🎤 microphone button to speak
2. **Select Language**: Choose Tamil, English, or Both
3. **Choose Style**: Select poem style (Free Verse, Haiku, etc.)
4. **Select Mood**: Choose the mood (Happy, Sad, Romantic, etc.)
5. **Generate**: Click "Generate Poem" button
6. **Listen**: Use the audio player to hear the poem read aloud
7. **Download**: Download the audio files

## 🎨 Poem Styles

| Style | Description |
|-------|-------------|
| Free Verse | No structure constraints |
| Haiku | 5-7-5 syllable pattern (Japanese) |
| Sonnet | 14-line poetic form (Shakespearean) |
| Limerick | 5-line humorous poem |
| Acrostic | First letters of each line spell a word |
| Ballad | Narrative poem with refrains |

## 🎭 Moods

- Neutral
- Happy
- Sad
- Romantic
- Inspirational
- Mysterious
- Peaceful

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health check |
| `/health` | GET | Health status |
| `/generate-poem` | POST | Generate poem |

### Example API Request

```json
POST /generate-poem
{
    "topic": "Love",
    "language": "both",
    "style": "free verse",
    "mood": "romantic"
}
```

## 📁 Project Structure

```
.
├── main.py              # FastAPI backend
├── app.py               # Streamlit frontend
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## ⚠️ Note

- Voice input requires a working microphone
- Make sure your microphone is not being used by another application
- For best results, speak clearly and in a quiet environment

## 🔨 Troubleshooting

### Voice Input Issues
- Install PyAudio: `pip install pyaudio`
- On Windows, you may need to install the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### API Connection Error
- Ensure FastAPI is running on port 8000
- Check firewall settings

### OpenAI API Error
- Verify the API key is valid
- Check your OpenAI account has credits

## 📄 License

MIT License - Feel free to use and modify!

---

Made with ❤️ using FastAPI, Streamlit, and OpenAI

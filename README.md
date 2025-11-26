# 🎓 ATMU AI Assistant - Uzbek Voice AI

An intelligent voice assistant for Axborot Texnologiyalari va Menejment Universiteti (ATMU) with multilingual TTS support and RAG-powered responses.

## ✨ Features

- **Dual Assistant Modes:**
  - **Assistant 1:** Browser-based TTS (fast, lightweight)
  - **Assistant 2:** High-quality Uzbek voice using `facebook/mms-tts-uzb-script_cyrillic`
- **RAG-Powered Responses:** Semantic search over university knowledge base
- **Smart Caching:** In-memory LRU cache for faster responses
- **Audio Interruption:** Instant stop when user starts typing or speaking
- **Natural Conversations:** Clean responses without repetitive phrases
- **Session Management:** Conversation history tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (optional, for local development)
- OpenAI or Google Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Tursunov-Akhmadjon/voice-AI.git
cd atmu-ai-assistant
```

2. **Set up backend**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```env
LLM_PROVIDER=openai  # or gemini
LLM_API_KEY=your_actual_api_key_here
```

4. **Run the server**
```bash
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

5. **Open the application**

Navigate to http://127.0.0.1:8001 in your browser

## 📁 Project Structure

```
voice AI/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (not in git)
│   ├── .env.example           # Example environment config
│   ├── university_data.txt    # Knowledge base
│   └── services/
│       ├── llm_service.py     # LLM integration (OpenAI/Gemini)
│       ├── tts_service.py     # Text-to-Speech service
│       ├── rag_service.py     # Semantic search & embeddings
│       ├── cache_service.py   # Response caching
│       └── conversation_service.py  # Session management
├── frontend/
│   ├── index.html             # Main UI
│   ├── style.css              # Styling
│   └── app.js                 # Frontend logic
└── .gitignore                 # Git ignore rules
```

## 🔒 Security

**IMPORTANT:** Never commit your `.env` file to version control!

The `.gitignore` file is configured to exclude:
- `.env` files (contains API keys)
- Python cache (`__pycache__/`)
- Virtual environments
- TTS model cache
- IDE configuration files

## 🌐 Deployment

### Option 1: Heroku

1. Create a `Procfile` in the root directory:
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set LLM_PROVIDER=openai
heroku config:set LLM_API_KEY=your_api_key
git push heroku main
```

### Option 2: Railway

1. Connect your GitHub repo to Railway
2. Add environment variables in Railway dashboard:
   - `LLM_PROVIDER`
   - `LLM_API_KEY`
3. Railway will auto-detect and deploy

### Option 3: Docker

Create `Dockerfile` in the root:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend backend
COPY frontend frontend
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

Build and run:
```bash
docker build -t atmu-ai .
docker run -p 8001:8001 -e LLM_PROVIDER=openai -e LLM_API_KEY=your_key atmu-ai
```

### Option 4: VPS (DigitalOcean, AWS, etc.)

1. SSH into your server
2. Clone the repository
3. Set up environment variables
4. Install dependencies
5. Run with systemd or supervisor for auto-restart

Example systemd service (`/etc/systemd/system/atmu-ai.service`):
```ini
[Unit]
Description=ATMU AI Assistant
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/atmu-ai/backend
Environment="LLM_PROVIDER=openai"
Environment="LLM_API_KEY=your_key"
ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable atmu-ai
sudo systemctl start atmu-ai
```

## 🧪 Testing

Run the test suite:
```bash
cd backend
python test_all.py
```

Tests verify:
- Markdown cleaning in Assistant 1
- Audio generation for Assistant 2
- Caching functionality

## 🛠️ Development

### Adding New Knowledge

Edit `backend/university_data.txt` to add new information about the university.

### Changing TTS Model

Modify `backend/services/tts_service.py` to use a different model:
```python
self.model_name = "your-model-name"
```

### API Endpoints

- `GET /` - Main application
- `POST /chat` - Send message, get response
- `GET /api/session` - Create new session
- `GET /api/cache/stats` - Cache statistics

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM service to use | `openai` or `gemini` |
| `LLM_API_KEY` | Your API key | `sk-...` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Facebook MMS TTS for Uzbek voice synthesis
- OpenAI/Google for LLM services
- FastAPI for the backend framework

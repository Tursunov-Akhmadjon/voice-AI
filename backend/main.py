from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()
from services.llm_service import llm_service, transliterate_to_cyrillic
from services.rag_service import rag_service
from services.cache_service import cache_service
from services.conversation_service import conversation_service
from services.tts_service import tts_service
app = FastAPI()
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")
class ChatRequest(BaseModel):
    message: str
    session_id: str = None
    version: int = 1  # 1 = Assistant 1 (Browser TTS), 2 = Assistant 2 (Backend TTS)
@app.get("/")
@app.head("/")
async def read_index():
    return FileResponse('../frontend/index.html')
@app.get("/api/session")
async def create_session():
    """Create new conversation session"""
    session_id = conversation_service.create_session()
    return {"session_id": session_id}
@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return cache_service.get_stats()
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Optimized chat endpoint with caching and semantic search
    
    Flow:
    1. Check cache for answer
    2. If cache miss, use semantic RAG to get context
    3. Get LLM response with conversation history
    4. Cache the result
    5. Update conversation history
    """
    user_message = request.message
    session_id = request.session_id
    version = request.version
    
    # Step 1: Check cache
    cached_answer = cache_service.get(user_message)
    if cached_answer:
        print(f"[CACHE HIT] {user_message[:50]}...")
        audio_base64 = None
        if version == 2:
            try:
                cyrillic = transliterate_to_cyrillic(cached_answer)
                audio_base64 = tts_service.generate_audio(cyrillic)
            except Exception as e:
                print(f"Error generating audio for cached response: {e}")
        return {"response": cached_answer, "cached": True, "audio": audio_base64}
    
    print(f"[CACHE MISS] {user_message[:50]}...")
    
    # Step 2: Get relevant context using semantic search
    # Pass OpenAI client for embeddings
    context = rag_service.get_relevant_context(
        user_message, 
        client=llm_service.client if hasattr(llm_service, 'client') else None
    )
    
    # Step 3: Get conversation history
    history = conversation_service.get_history(session_id) if session_id else []
    
    # Step 4: Get LLM response
    # Always returns Latin text now, we handle Cyrillic internally for TTS
    result = llm_service.get_response(user_message, context, history, version=version)
    response_text = result['text']
    
    # Generate audio for version 2
    audio_base64 = None
    if version == 2:
        cyrillic_text = result.get('cyrillic')
        if cyrillic_text:
             audio_base64 = tts_service.generate_audio(cyrillic_text)
    
    # Step 5: Cache the result (text only)
    cache_service.set(user_message, response_text)
    
    # Step 6: Update conversation history
    if session_id:
        conversation_service.add_message(session_id, "user", user_message)
        conversation_service.add_message(session_id, "assistant", response_text)
    
    return {"response": response_text, "cached": False, "audio": audio_base64}

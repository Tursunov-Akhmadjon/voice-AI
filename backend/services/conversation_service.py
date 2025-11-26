from typing import Dict, List
import uuid
import time

class ConversationService:
    """
    Manages conversation history per session
    Time Complexity: O(1) for operations
    Space Complexity: O(s * m) where s = sessions, m = max_messages
    """
    def __init__(self, max_messages: int = 5, session_timeout: int = 1800):
        self.sessions: Dict[str, Dict] = {}
        self.max_messages = max_messages
        self.session_timeout = session_timeout  # 30 minutes
    
    def create_session(self) -> str:
        """Create new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "messages": [],
            "last_activity": time.time()
        }
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session history"""
        if session_id not in self.sessions:
            session_id = self.create_session()
        
        session = self.sessions[session_id]
        session["messages"].append({
            "role": role,
            "content": content
        })
        
        # Keep only last N messages
        if len(session["messages"]) > self.max_messages * 2:  # *2 for user+assistant pairs
            session["messages"] = session["messages"][-self.max_messages * 2:]
        
        session["last_activity"] = time.time()
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for session"""
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        
        # Check if expired
        if time.time() - session["last_activity"] > self.session_timeout:
            del self.sessions[session_id]
            return []
        
        return session["messages"]
    
    def cleanup_expired(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired = [
            sid for sid, session in self.sessions.items()
            if current_time - session["last_activity"] > self.session_timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]

# Global instance
conversation_service = ConversationService()

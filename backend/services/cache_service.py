import hashlib
import time
from typing import Optional, Dict
from collections import OrderedDict

class CacheService:
    """
    LRU Cache for Q&A pairs
    Time Complexity: O(1) for get/set
    Space Complexity: O(n) where n = max_size
    """
    def __init__(self, max_size: int = 100, ttl_seconds: int = 86400):
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds  # 24 hours default
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def _hash_question(self, question: str) -> str:
        """Generate hash for question (case-insensitive, normalized)"""
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, question: str) -> Optional[str]:
        """
        Get cached answer for question
        Returns None if not found or expired
        """
        key = self._hash_question(question)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if time.time() - entry["timestamp"] > self.ttl_seconds:
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            return entry["answer"]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, question: str, answer: str):
        """Add question-answer pair to cache"""
        key = self._hash_question(question)
        
        # If already exists, update and move to end
        if key in self.cache:
            self.cache.move_to_end(key)
        
        # Add new entry
        self.cache[key] = {
            "question": question,
            "answer": answer,
            "timestamp": time.time()
        }
        
        # Evict oldest if over capacity
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)  # Remove oldest (first item)
            self.stats["evictions"] += 1
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "hit_rate": f"{hit_rate:.1f}%"
        }
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()

# Global instance
cache_service = CacheService()

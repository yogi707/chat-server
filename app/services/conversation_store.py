"""
Conversation Store Service

This service provides in-memory storage for conversation history,
allowing the AI to maintain context across multiple interactions
within a conversation session.
"""

import threading
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    """
    Represents a single message in a conversation.
    """
    query: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """
    Represents a complete conversation with its history and metadata.
    """
    conversation_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, query: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a new message to the conversation."""
        print(len(self.messages))
        message = ConversationMessage(
            query=query,
            response=response,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_accessed = datetime.now()
    
    def get_context_for_gemini(self, include_last_n: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation context formatted for Gemini API.
        Returns list of user/model message pairs.
        """
        context = []
        # Get last N messages to avoid token limits
        recent_messages = self.messages[-include_last_n:] if include_last_n > 0 else self.messages
        
        for message in recent_messages:
            # Add user message
            context.append({
                "role": "user",
                "parts": [{"text": message.query}]
            })
            # Add model response
            context.append({
                "role": "model", 
                "parts": [{"text": message.response}]
            })
        
        return context
    
    def get_last_message(self) -> Optional[ConversationMessage]:
        """Get the last message in the conversation."""
        return self.messages[-1] if self.messages else None
    
    def message_count(self) -> int:
        """Get the total number of messages in the conversation."""
        return len(self.messages)


class ConversationStore:
    """
    Thread-safe in-memory storage for conversation histories.
    
    Features:
    - Thread-safe operations using locks
    - Automatic cleanup of old conversations
    - Configurable memory limits
    - Conversation statistics and monitoring
    """
    
    def __init__(
        self,
        max_conversations: int = 1000,
        max_conversation_age_hours: int = 24,
        cleanup_interval_seconds: int = 3600  # 1 hour
    ):
        """
        Initialize the conversation store.
        
        Args:
            max_conversations: Maximum number of conversations to keep in memory
            max_conversation_age_hours: Maximum age of conversations before cleanup
            cleanup_interval_seconds: How often to run cleanup (in seconds)
        """
        self._conversations: Dict[str, Conversation] = {}
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        
        # Configuration
        self.max_conversations = max_conversations
        self.max_conversation_age = timedelta(hours=max_conversation_age_hours)
        self.cleanup_interval = cleanup_interval_seconds
        
        # Statistics
        self._stats = {
            "total_conversations_created": 0,
            "total_messages_stored": 0,
            "conversations_cleaned_up": 0,
            "last_cleanup": None
        }
        
        # Start background cleanup
        self._start_cleanup_thread()
        
        logger.info(f"ConversationStore initialized with max_conversations={max_conversations}, "
                   f"max_age={max_conversation_age_hours}h")
    
    def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            conversation_id: Optional custom conversation ID. If None, generates UUID.
            
        Returns:
            str: The conversation ID
        """
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        with self._lock:
            if conversation_id in self._conversations:
                logger.warning(f"Conversation {conversation_id} already exists, returning existing")
                return conversation_id
            
            self._conversations[conversation_id] = Conversation(conversation_id=conversation_id)
            self._stats["total_conversations_created"] += 1
            
            # Check if we need to cleanup due to memory limits
            if len(self._conversations) > self.max_conversations:
                self._cleanup_old_conversations(force=True)
            
            logger.info(f"Created new conversation: {conversation_id}")
            return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            query: User's query/prompt
            response: AI's response
            metadata: Optional metadata for the message
            
        Returns:
            bool: True if message was added successfully, False if conversation not found
        """
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return False
            
            conversation.add_message(query, response, metadata)
            self._stats["total_messages_stored"] += 1
            
            logger.debug(f"Added message to conversation {conversation_id}, "
                        f"total messages: {conversation.message_count()}")
            return True
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Optional[Conversation]: The conversation or None if not found
        """
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation:
                conversation.last_accessed = datetime.now()
            return conversation
    
    def get_conversation_context(
        self,
        conversation_id: str,
        include_last_n: int = 10
    ) -> Optional[List[Dict[str, str]]]:
        """
        Get conversation context formatted for Gemini API.
        
        Args:
            conversation_id: ID of the conversation
            include_last_n: Number of recent messages to include (0 for all)
            
        Returns:
            Optional[List[Dict[str, str]]]: Context for Gemini API or None if conversation not found
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return conversation.get_context_for_gemini(include_last_n)
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """
        Check if a conversation exists.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            bool: True if conversation exists
        """
        with self._lock:
            return conversation_id in self._conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: ID of the conversation to delete
            
        Returns:
            bool: True if conversation was deleted, False if not found
        """
        with self._lock:
            if conversation_id in self._conversations:
                del self._conversations[conversation_id]
                logger.info(f"Deleted conversation: {conversation_id}")
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get store statistics.
        
        Returns:
            Dict[str, Any]: Statistics about the store
        """
        with self._lock:
            return {
                **self._stats,
                "active_conversations": len(self._conversations),
                "max_conversations": self.max_conversations,
                "max_conversation_age_hours": self.max_conversation_age.total_seconds() / 3600,
            }
    
    def clear_all(self) -> int:
        """
        Clear all conversations from the store.
        
        Returns:
            int: Number of conversations that were cleared
        """
        with self._lock:
            count = len(self._conversations)
            self._conversations.clear()
            logger.info(f"Cleared all {count} conversations from store")
            return count
    
    def _cleanup_old_conversations(self, force: bool = False) -> int:
        """
        Clean up old conversations based on age and memory limits.
        
        Args:
            force: If True, cleanup even if interval hasn't passed
            
        Returns:
            int: Number of conversations cleaned up
        """
        now = datetime.now()
        
        # Check if cleanup interval has passed (unless forced)
        if not force and self._stats["last_cleanup"]:
            time_since_cleanup = (now - self._stats["last_cleanup"]).total_seconds()
            if time_since_cleanup < self.cleanup_interval:
                return 0
        
        with self._lock:
            conversations_to_remove = []
            
            # Find conversations to remove based on age
            cutoff_time = now - self.max_conversation_age
            for conv_id, conversation in self._conversations.items():
                if conversation.last_accessed < cutoff_time:
                    conversations_to_remove.append(conv_id)
            
            # If still over limit, remove oldest conversations
            if len(self._conversations) - len(conversations_to_remove) > self.max_conversations:
                # Sort by last_accessed time and remove oldest
                remaining_conversations = [
                    (conv_id, conv) for conv_id, conv in self._conversations.items()
                    if conv_id not in conversations_to_remove
                ]
                remaining_conversations.sort(key=lambda x: x[1].last_accessed)
                
                excess_count = len(remaining_conversations) - self.max_conversations
                if excess_count > 0:
                    for conv_id, _ in remaining_conversations[:excess_count]:
                        conversations_to_remove.append(conv_id)
            
            # Remove conversations
            for conv_id in conversations_to_remove:
                del self._conversations[conv_id]
            
            self._stats["conversations_cleaned_up"] += len(conversations_to_remove)
            self._stats["last_cleanup"] = now
            
            if conversations_to_remove:
                logger.info(f"Cleaned up {len(conversations_to_remove)} old conversations")
            
            return len(conversations_to_remove)
    
    def _start_cleanup_thread(self) -> None:
        """Start the background cleanup thread."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self.cleanup_interval)
                    self._cleanup_old_conversations()
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("Started background cleanup thread")


# Global instance
conversation_store = ConversationStore()
"""
Gemini AI Service

This service handles integration with Google's Gemini AI API for generating
AI-powered responses to user queries. It provides both regular and streaming
responses with proper async support and error handling.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, AsyncGenerator
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.schemas.streaming import  StreamingChunk

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service class for interacting with Google's Gemini AI API.
    
    This service provides methods to generate AI responses using Gemini models
    with proper error handling and configuration management.
    """
    
    def __init__(self):
        """Initialize the Gemini service with API configuration."""
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.model = None
        
        if self.api_key:
            self._configure_api()
        else:
            logger.warning("Gemini API key not configured")
    
    def _configure_api(self) -> None:
        """Configure the Gemini API with the provided API key."""
        try:
            genai.configure(api_key=self.api_key)
            
            # Configure safety settings to be less restrictive for general chat
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=safety_settings
            )
            
            logger.info(f"Gemini API configured successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise
    
    async def generate_response(self, query: str) -> Dict[str, Any]:
        """
        Generate a response to a user query using Gemini AI.
        
        Args:
            query (str): The user's question or prompt
            
        Returns:
            Dict[str, Any]: Response containing the generated text and metadata
            
        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
        """
        if not self.api_key:
            raise ValueError("Gemini API key is not configured")
        
        if not self.model:
            raise ValueError("Gemini model is not initialized")
        
        try:
            logger.info(f"Generating response for query: {query[:100]}...")
            
            # Generate response using Gemini
            response = await self._generate_content_async(query)
            
            # Extract response text
            response_text = response.text if response.text else "No response generated"
            
            # Prepare response data
            result = {
                "response": response_text,
                "model": self.model_name,
                "usage": {
                    "prompt_tokens": len(query.split()),  # Rough estimation
                    "completion_tokens": len(response_text.split()),  # Rough estimation
                }
            }
            
            logger.info("Successfully generated Gemini response")
            return result
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def _generate_content_async(self, query: str):
        """
        Asynchronously generate content using Gemini.
        
        Uses asyncio.run_in_executor to run the synchronous Gemini API
        in a thread pool to avoid blocking the event loop.
        """
        try:
            loop = asyncio.get_event_loop()
            # Run the synchronous API call in a thread pool
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(query)
            )
            return response
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise
    
    def generate_stream(self, query: str):
        """
        Generate a streaming response to a user query using Gemini AI.
        
        This method yields chunks of the response as they're generated,
        allowing for real-time streaming to the client.
        
        Args:
            query (str): The user's question or prompt
            
        Yields:
            Dict[str, Any]: Chunks of the response containing text and metadata
            
        Raises:
            ValueError: If API key is not configured
            Exception: If API call fails
        """
        if not self.api_key:
            raise ValueError("Gemini API key is not configured")
        
        if not self.model:
            raise ValueError("Gemini model is not initialized")
        
        try:
            logger.info(f"Received streaming query request: {query[:100]}...")
            response = self.model.generate_content(query, stream=True)
            for chunk_data  in response:
                chunk = StreamingChunk(**{
                        "text": chunk_data.text,
                        "model": self.model_name,
                        "done": False
                    })
                chunk_json = chunk.model_dump_json()
                if chunk.text:
                    yield f"data: {chunk_json}\n\n"
            yield f"data: {StreamingChunk(text='', model=gemini_service.model_name, done=True).model_dump_json()}\n\n"
                
        except Exception as e:
            logger.error(f"Error in streaming Gemini response: {str(e)}")
            # Send error chunk
            yield f"data: {StreamingChunk(text='', model=self.model_name, error=str(e), done=True).model_dump_json()}\n\n"
    

    def is_configured(self) -> bool:
        """
        Check if the Gemini service is properly configured.
        
        Returns:
            bool: True if API key is set and model is initialized
        """
        return self.api_key is not None and self.model is not None


# Create a global instance of the service
gemini_service = GeminiService()
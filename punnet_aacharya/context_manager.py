import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

class ConversationContextManager:
    def __init__(self):
        logger.info("Initializing ConversationContextManager")
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is required but not found")
            raise ValueError("GEMINI_API_KEY is required")
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            logger.info(f"Gemini model initialized: {GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {str(e)}")
            raise
        
        logger.info("ConversationContextManager initialized successfully")
    
    def get_conversation_history(self, user_id: int, username: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for a user"""
        try:
            from chat_logger import ChatLogger
            chat_logger = ChatLogger()
            
            # Get recent messages
            recent_messages = chat_logger.get_recent_messages(username, user_id, limit)
            
            # Format for LLM consumption
            formatted_history = []
            for msg in recent_messages:
                formatted_history.append({
                    "role": "user" if msg["message_type"] == "user" else "assistant",
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "context": msg.get("metadata", {}).get("context", "general")
                })
            
            logger.info(f"Retrieved {len(formatted_history)} messages for user {user_id}")
            return formatted_history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def analyze_context_and_prepare_response(self, 
                                          user_message: str, 
                                          chart_data: Optional[Dict], 
                                          user_name: str,
                                          conversation_history: List[Dict]) -> Dict:
        """
        First LLM call: Analyze context and prepare response structure
        Returns a JSON with context analysis and response guidelines
        """
        logger.info("Analyzing conversation context and preparing response structure")
        
        # Prepare conversation history for analysis
        history_text = ""
        if conversation_history:
            history_text = "Previous Conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n"
        
        # Prepare chart context
        chart_context = ""
        if chart_data:
            try:
                chart = json.loads(chart_data) if isinstance(chart_data, str) else chart_data
                planets = chart.get('planets', {})
                houses = chart.get('houses', {})
                dasha = chart.get('dasha', {})
                
                chart_context = f"""Chart Information:
Ascendant: {chart.get('ascendant', 'Unknown')}
Current Dasha: {dasha.get('current_dasha', 'Unknown')}
Key Planets:"""
                
                key_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
                for planet in key_planets:
                    if planet in planets:
                        planet_data = planets[planet]
                        sign = planet_data.get('sign', 'Unknown')
                        house = planet_data.get('house', 'Unknown')
                        chart_context += f"\n{planet}: {sign} (House {house})"
            except Exception as e:
                logger.error(f"Error formatting chart context: {str(e)}")
                chart_context = "Chart data available but formatting error occurred."
        
        # Create analysis prompt
        analysis_prompt = f"""You are Punnet Aacharya, a wise Vedic astrologer. Analyze the conversation context and prepare a response structure.

Current User Message: "{user_message}"
User Name: {user_name}

{history_text}

{chart_context}

Analyze the conversation and provide a JSON response with the following structure. IMPORTANT: Return ONLY valid JSON, no other text:

{{
    "extracted_birth_details": {{
        "name": "(if found, else null)",
        "birth_date": "(if found, else null)",
        "birth_time": "(if found, else null)",
        "birth_place": "(if found, else null)"
    }},
    "context_analysis": {{
        "user_concern": "What the user is asking about",
        "conversation_flow": "How the conversation has progressed",
        "previous_topics": ["list of previously discussed topics"],
        "emotional_state": "User's apparent emotional state",
        "question_category": "career/marriage/health/education/general",
        "is_follow_up": true,
        "requires_clarification": false
    }},
    "response_guidelines": {{
        "tone": "caring",
        "focus_areas": ["specific areas to address"],
        "should_reference_history": false,
        "should_ask_follow_up": true,
        "response_length": "medium",
        "key_points": ["main points to cover in response"]
    }},
    "astrological_focus": {{
        "primary_aspect": "main astrological aspect to discuss",
        "supporting_aspects": ["other relevant aspects"],
        "timing_mention": false,
        "remedies_mention": false
    }}
}}

CRITICAL: Return ONLY the JSON object above, no explanations, no markdown formatting, no additional text. If you find any birth details in the conversation, fill them in the 'extracted_birth_details' field."""

        try:
            logger.info("Sending context analysis request to Gemini")
            start_time = datetime.now()
            response = self.model.generate_content(analysis_prompt)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            logger.info(f"Context analysis received in {response_time:.2f} seconds")
            
            # Parse JSON response with error handling
            response_text = response.text.strip()
            
            # Try to extract JSON if there's extra text
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            try:
                analysis_result = json.loads(response_text)
                logger.info(f"Context analysis completed: {analysis_result.get('context_analysis', {}).get('question_category', 'unknown')}")
                return analysis_result
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                logger.error(f"Response text: {response_text[:200]}...")
                raise
            
        except Exception as e:
            logger.error(f"Error in context analysis: {str(e)}")
            # Return default structure
            return {
                "extracted_birth_details": {
                    "name": None,
                    "birth_date": None,
                    "birth_time": None,
                    "birth_place": None
                },
                "context_analysis": {
                    "user_concern": user_message,
                    "conversation_flow": "new conversation",
                    "previous_topics": [],
                    "emotional_state": "neutral",
                    "question_category": "general",
                    "is_follow_up": False,
                    "requires_clarification": False
                },
                "response_guidelines": {
                    "tone": "caring",
                    "focus_areas": ["general guidance"],
                    "should_reference_history": False,
                    "should_ask_follow_up": True,
                    "response_length": "medium",
                    "key_points": ["acknowledge concern", "provide guidance"]
                },
                "astrological_focus": {
                    "primary_aspect": "general",
                    "supporting_aspects": [],
                    "timing_mention": False,
                    "remedies_mention": False
                }
            }
    
    def generate_contextual_response(self, 
                                   user_message: str,
                                   chart_data: Optional[Dict],
                                   user_name: str,
                                   context_analysis: Dict) -> str:
        """
        Second LLM call: Generate the final response using context analysis
        """
        logger.info("Generating contextual response using analysis")
        
        # Prepare chart context
        chart_context = ""
        if chart_data:
            try:
                chart = json.loads(chart_data) if isinstance(chart_data, str) else chart_data
                planets = chart.get('planets', {})
                houses = chart.get('houses', {})
                dasha = chart.get('dasha', {})
                
                chart_context = f"""Chart Information for {user_name}:
Ascendant: {chart.get('ascendant', 'Unknown')}
Current Dasha: {dasha.get('current_dasha', 'Unknown')}

Key Planetary Positions:"""
                
                key_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
                for planet in key_planets:
                    if planet in planets:
                        planet_data = planets[planet]
                        sign = planet_data.get('sign', 'Unknown')
                        house = planet_data.get('house', 'Unknown')
                        chart_context += f"\n{planet}: {sign} (House {house})"
            except Exception as e:
                logger.error(f"Error formatting chart context: {str(e)}")
                chart_context = "Chart data available but formatting error occurred."
        
        # Create response prompt using context analysis
        response_prompt = f"""You are Punnet Aacharya, a wise and experienced Vedic astrologer from India. You speak in a warm, spiritual, and authoritative manner, using Hindi naturally mixed with English.

Context Analysis:
{json.dumps(context_analysis, indent=2)}

Current User Message: "{user_message}"
User Name: {user_name}

{chart_context}

Based on the context analysis, generate a warm, caring response that:
1. Acknowledges the user's concern with empathy
2. References previous conversation if relevant
3. Provides astrological guidance based on the chart
4. Uses the specified tone and focus areas
5. Includes timing and remedies if mentioned in analysis
6. Maintains the caring guru personality throughout

IMPORTANT GUIDELINES:
- Keep response under 3000 characters
- Use natural Hindi-English mix
- Be conversational, not robotic
- Show empathy and understanding
- Make predictions feel personal and relevant
- Use simple language that anyone can understand
- Maintain the warm, caring guru personality

Generate a natural, conversational response that feels like a caring guru speaking to their disciple."""

        try:
            logger.info("Sending contextual response request to Gemini")
            start_time = datetime.now()
            response = self.model.generate_content(response_prompt)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            logger.info(f"Contextual response received in {response_time:.2f} seconds")
            logger.info(f"Response length: {len(response.text)} characters")
            
            # Check if response is too long and truncate if necessary
            if len(response.text) > 3000:
                logger.warning(f"Response too long ({len(response.text)} chars), truncating to 3000")
                response.text = response.text[:2997] + "..."
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating contextual response: {str(e)}")
            return f"Maaf kijiye Beta, kuch technical problem aa raha hai. Aap thoda der baad dobara try karein. Main aapki help karunga. 🙏"
    
    def process_user_message(self, 
                           user_message: str,
                           chart_data: Optional[Dict],
                           user_name: str,
                           user_id: int,
                           username: str) -> Tuple[str, Dict]:
        """
        Main method to process user message with full context awareness
        Returns: (response_text, context_analysis)
        """
        logger.info(f"Processing user message with context: '{user_message[:50]}...'")
        
        try:
            # Step 1: Get conversation history
            conversation_history = self.get_conversation_history(user_id, username, limit=10)
            logger.info(f"Retrieved {len(conversation_history)} historical messages")
            
            # Step 2: Analyze context and prepare response structure
            context_analysis = self.analyze_context_and_prepare_response(
                user_message, chart_data, user_name, conversation_history
            )
            
            # Step 3: Generate contextual response
            response_text = self.generate_contextual_response(
                user_message, chart_data, user_name, context_analysis
            )
            
            logger.info("Context-aware response generation completed successfully")
            return response_text, context_analysis
            
        except Exception as e:
            logger.error(f"Error in context-aware processing: {str(e)}")
            fallback_response = "Maaf kijiye Beta, kuch technical problem aa raha hai. Aap thoda der baad dobara try karein. Main aapki help karunga. 🙏"
            return fallback_response, {} 
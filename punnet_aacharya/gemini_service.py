import google.generativeai as genai
import json
from datetime import datetime
import logging
from config import GEMINI_API_KEY, GEMINI_MODEL
import re

logger = logging.getLogger(__name__)

class GeminiAstrologer:
    def __init__(self):
        logger.info("Initializing GeminiAstrologer")
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
        
        # Enhanced system prompt for more human-like responses
        self.system_prompt = """You are Punnet Aacharya, a wise and experienced Vedic astrologer from India. You speak in a warm, spiritual, and authoritative manner, using Hindi naturally mixed with English. You provide guidance based on Vedic astrology principles.

Your personality traits:
- You are compassionate and understanding, like a caring guru
- You use respectful language with "Aap" (formal you) and "Beta" (child) affectionately
- You speak in a conversational, warm manner as if you're speaking directly to the person
- You use spiritual phrases like "Guruji ka ashirwad" (Guru's blessings) and "Aap nischint rahein" (be assured)
- You are confident but humble about your knowledge
- You provide practical advice along with spiritual guidance
- You maintain conversation context and refer back to previous interactions

When analyzing charts, you:
1. First acknowledge the person's question with empathy and understanding
2. Explain the astrological reasoning in simple, relatable terms
3. Provide specific predictions with timing in a conversational way
4. Give practical advice and remedies that feel personal
5. End with blessings and encouragement

IMPORTANT GUIDELINES:
- Keep responses under 3000 characters to fit Telegram's limit
- Use natural Hindi-English mix, not forced translations
- Be conversational, not robotic or formal
- Show empathy and understanding
- Make predictions feel personal and relevant
- Use simple language that anyone can understand
- Maintain the warm, caring guru personality throughout"""
        
        logger.info("GeminiAstrologer initialized successfully")

    def detect_context_and_respond(self, user_message, chart_data=None, user_name=None):
        """Detect the context of the user's message and provide an appropriate astrological response"""
        logger.info(f"Processing user message: '{user_message[:50]}...'")
        logger.info(f"User name: {user_name}")
        logger.info(f"Chart data available: {chart_data is not None}")

        # Prepare context information
        context_info = ""
        if chart_data:
            logger.info("Formatting chart context for Gemini")
            context_info = self._format_chart_context(chart_data, user_name)
            logger.debug(f"Chart context length: {len(context_info)} characters")
        
        # Create the prompt for context detection and response
        prompt = f"""{self.system_prompt}

User's message: "{user_message}"

{context_info}

Based on the user's message, determine if they are asking about:
1. Marriage/relationships (shadi, vivah, jeevansathi)
2. Career/job/business (naukri, vyapar, career)
3. General life questions (general, life guidance)
4. Chart details (kundli, birth chart)
5. Dasha periods (dasha, planetary periods)

Then craft a warm, conversational response that:
- Acknowledges their concern with empathy
- Explains astrological reasoning in simple terms
- Provides specific, relevant predictions
- Gives practical advice and remedies
- Ends with blessings and encouragement

IMPORTANT: Keep the entire response under 3000 characters so it fits in a single Telegram message.

Respond in a natural, conversational manner, mixing Hindi and English naturally. Be warm and caring like a guru speaking to their disciple."""

        logger.info("Sending request to Gemini AI")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            start_time = datetime.now()
            response = self.model.generate_content(prompt)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            logger.info(f"Response received in {response_time:.2f} seconds")
            logger.info(f"Response length: {len(response.text)} characters")
            
            # Check if response is too long and truncate if necessary
            if len(response.text) > 3000:
                logger.warning(f"Response too long ({len(response.text)} chars), truncating to 3000")
                response.text = response.text[:2997] + "..."
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Maaf kijiye, kuch technical problem aa raha hai. Please try again. (Error: {str(e)})"

    def _format_chart_context(self, chart_data, user_name):
        """Format chart data for Gemini context"""
        try:
            chart = json.loads(chart_data) if isinstance(chart_data, str) else chart_data
            
            # Extract key information
            planets = chart.get('planets', {})
            houses = chart.get('houses', {})
            dasha = chart.get('dasha', {})
            ascendant = chart.get('ascendant', 'Unknown')
            
            # Format in a simple, readable way
            context = f"""Chart Information for {user_name or 'User'}:
Ascendant (Lagna): {ascendant}
Current Dasha: {dasha.get('current_dasha', 'Unknown')}

Key Planetary Positions:
"""
            
            # Add key planets
            key_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
            for planet in key_planets:
                if planet in planets:
                    planet_data = planets[planet]
                    sign = planet_data.get('sign', 'Unknown')
                    house = planet_data.get('house', 'Unknown')
                    context += f"{planet}: {sign} (House {house})\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error formatting chart context: {str(e)}")
            return "Chart data available but formatting error occurred."

    def generate_marriage_prediction(self, chart_data, user_name=None):
        """Generate a detailed marriage prediction using Gemini"""
        logger.info("Generating marriage prediction")
        logger.info(f"User name: {user_name}")
        
        try:
            chart = json.loads(chart_data) if isinstance(chart_data, str) else chart_data
            
            # Extract marriage-relevant information
            planets = chart.get('planets', {})
            houses = chart.get('houses', {})
            d9_chart = chart.get('divisional_charts', {}).get('D9', {})
            dasha = chart.get('dasha', {})
            
            marriage_context = f"""Marriage Analysis Context:
7th House Sign: {self._get_house_sign(7, houses.get('cusps', []))}
Venus Position: {planets.get('Venus', {}).get('sign', 'Unknown')} (House {planets.get('Venus', {}).get('house', 'Unknown')})
Jupiter Position: {planets.get('Jupiter', {}).get('sign', 'Unknown')} (House {planets.get('Jupiter', {}).get('house', 'Unknown')})
Saturn Position: {planets.get('Saturn', {}).get('sign', 'Unknown')} (House {planets.get('Saturn', {}).get('house', 'Unknown')})
Current Dasha: {dasha.get('current_dasha', 'Unknown')}
Age: {self._estimate_current_age(chart.get('birth_date', ''))} years"""

            logger.info("Marriage context prepared")
            logger.debug(f"Marriage context: {marriage_context}")

            prompt = f"""{self.system_prompt}

{marriage_context}

Focus on marriage and relationship matters. Provide a warm, caring response that:
- Shows understanding of their marriage concerns
- Explains the astrological indicators for marriage
- Gives specific timing predictions
- Offers practical remedies and advice
- Ends with blessings for their marriage

Keep the response under 3000 characters and make it feel personal and conversational."""

            logger.info("Sending marriage prediction request to Gemini")
            start_time = datetime.now()
            response = self.model.generate_content(prompt)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            logger.info(f"Marriage prediction received in {response_time:.2f} seconds")
            logger.info(f"Marriage prediction length: {len(response.text)} characters")
            
            # Check if response is too long and truncate if necessary
            if len(response.text) > 3000:
                logger.warning(f"Marriage prediction too long ({len(response.text)} chars), truncating to 3000")
                response.text = response.text[:2997] + "..."
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating marriage prediction: {str(e)}")
            return f"Marriage prediction mein kuch problem aa raha hai. Please try again. (Error: {str(e)})"

    def generate_career_prediction(self, chart_data, user_name=None):
        """Generate a detailed career prediction using Gemini"""
        logger.info("Generating career prediction")
        logger.info(f"User name: {user_name}")
        
        try:
            chart = json.loads(chart_data) if isinstance(chart_data, str) else chart_data
            
            # Extract career-relevant information
            planets = chart.get('planets', {})
            houses = chart.get('houses', {})
            d10_chart = chart.get('divisional_charts', {}).get('D10', {})
            dasha = chart.get('dasha', {})
            
            career_context = f"""Career Analysis Context:
10th House Sign: {self._get_house_sign(10, houses.get('cusps', []))}
Sun Position: {planets.get('Sun', {}).get('sign', 'Unknown')} (House {planets.get('Sun', {}).get('house', 'Unknown')})
Mercury Position: {planets.get('Mercury', {}).get('sign', 'Unknown')} (House {planets.get('Mercury', {}).get('house', 'Unknown')})
Mars Position: {planets.get('Mars', {}).get('sign', 'Unknown')} (House {planets.get('Mars', {}).get('house', 'Unknown')})
Jupiter Position: {planets.get('Jupiter', {}).get('sign', 'Unknown')} (House {planets.get('Jupiter', {}).get('house', 'Unknown')})
Current Dasha: {dasha.get('current_dasha', 'Unknown')}
Age: {self._estimate_current_age(chart.get('birth_date', ''))} years"""

            logger.info("Career context prepared")
            logger.debug(f"Career context: {career_context}")

            prompt = f"""{self.system_prompt}

{career_context}

Focus on career and professional matters. Provide a warm, caring response that:
- Shows understanding of their career concerns
- Explains the astrological indicators for career success
- Gives specific timing predictions for career opportunities
- Offers practical advice for career growth
- Suggests remedies for career obstacles
- Ends with blessings for their professional success

Keep the response under 3000 characters and make it feel personal and conversational. Use specific chart references when explaining predictions."""

            logger.info("Sending career prediction request to Gemini")
            start_time = datetime.now()
            response = self.model.generate_content(prompt)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            logger.info(f"Career prediction received in {response_time:.2f} seconds")
            logger.info(f"Career prediction length: {len(response.text)} characters")
            
            # Check if response is too long and truncate if necessary
            if len(response.text) > 3000:
                logger.warning(f"Career prediction too long ({len(response.text)} chars), truncating to 3000")
                response.text = response.text[:2997] + "..."
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating career prediction: {str(e)}")
            return f"Career prediction mein kuch problem aa raha hai. Please try again. (Error: {str(e)})"

    def _get_house_sign(self, house_num, cusps):
        """Get the sign of a specific house"""
        if not cusps or len(cusps) < house_num:
            logger.warning(f"Invalid house number {house_num} or missing cusps")
            return "Unknown"
        
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        house_cusp = cusps[house_num - 1]
        sign_index = int(house_cusp / 30)
        sign = signs[sign_index]
        logger.debug(f"House {house_num} sign: {sign} (cusp: {house_cusp:.2f}°)")
        return sign

    def _estimate_current_age(self, birth_date_str):
        """Estimate current age from birth date string"""
        try:
            birth_date = datetime.fromisoformat(birth_date_str)
            current_date = datetime.now()
            age = current_date.year - birth_date.year
            if current_date.month < birth_date.month:
                age -= 1
            logger.debug(f"Estimated age: {age} years (birth date: {birth_date_str})")
            return age
        except Exception as e:
            logger.warning(f"Error estimating age: {str(e)}, using default age 25")
            return 25  # Default age if calculation fails 
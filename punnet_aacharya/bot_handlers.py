from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, ConversationHandler
)
import logging
from datetime import datetime
import json
import re

from database import get_db, User, Consultation
from astro_calculator import AstroCalculator
from vector_store import AstrologyKnowledgeBase
from gemini_service import GeminiAstrologer
from context_manager import ConversationContextManager
from chat_logger import ChatLogger
from prompts import BotPrompts
from config import BOT_NAME

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
ONBOARDING = 0
CONSULTATION = 1

class AstrologyBot:
    def __init__(self):
        logger.info("Initializing AstrologyBot")
        try:
            self.calculator = AstroCalculator()
            self.knowledge_base = AstrologyKnowledgeBase()
            self.prompts = BotPrompts()
            self.gemini_astrologer = GeminiAstrologer()
            self.context_manager = ConversationContextManager()
            self.chat_logger = ChatLogger()
            logger.info("AstrologyBot initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AstrologyBot: {str(e)}")
            raise
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        logger.info(f"Start command received from user {user.id} (@{user.username})")
        
        # Log user start command
        self.chat_logger.log_user_message(
            user.id, 
            user.username or "unknown", 
            "/start", 
            "command"
        )
        
        # Initialize user data
        context.user_data.clear()
        context.user_data['onboarding_state'] = 'start'
        context.user_data['birth_details'] = {}
        context.user_data['conversation_memory'] = {
            'asked_questions': [],
            'last_question': None,
            'last_category': None,
            'session_start': datetime.now().isoformat()
        }
        logger.info("User data initialized for new session")
        
        # Send welcome message from Puneet Guruji
        welcome_message = """🙏 नमस्ते! मैं हूँ Punnet Aacharya, आपका व्यक्तिगत वैदिक ज्योतिष सलाहकार।\n\nयहाँ आप मुझसे शादी, करियर, धन, शिक्षा, स्वास्थ्य, या जीवन के किसी भी पहलू पर मार्गदर्शन ले सकते हैं — वो भी आपकी जन्म कुंडली के आधार पर, पूरी तरह गोपनीय और निशुल्क।\n\nमुझे आपकी जन्म संबंधी जानकारी (नाम, जन्म तिथि, समय, स्थान) चाहिए ताकि मैं सटीक ज्योतिषीय सलाह दे सकूं।\n\n💡 आप मुझसे पूछ सकते हैं:\n• शादी कब होगी? जीवनसाथी कैसा होगा?\n• करियर में सफलता के योग\n• धन, स्वास्थ्य, शिक्षा, विदेश यात्रा, और बहुत कुछ!\n\nकृपया सबसे पहले अपना नाम बताएं — मैं आपकी पूरी मदद करूंगा। आप निश्चिंत रहें, सब अच्छा होगा! 📿\n\n\n---\n\n🙏 Hello! I am Punnet Aacharya, your personal Vedic astrology advisor.\n\nHere, you can ask me about marriage, career, money, education, health, or any aspect of life — all based on your birth chart, confidentially and for free.\n\nI need your birth details (name, date, time, place) to give you accurate astrological guidance.\n\n💡 You can ask me things like:\n• When will I get married? What will my partner be like?\n• Career success possibilities\n• Money, health, education, foreign travel, and much more!\n\nPlease tell me your name first — I am here to help you. Everything will be fine! 📿\n\n\nकृपया बताएं, आप किस भाषा में बात करना पसंद करेंगे? (Please tell me, which language do you prefer to speak in?)\n\nType 'Hindi' or 'English'.\n"""
        
        await update.message.reply_text(welcome_message)
        # Save that we are waiting for language preference
        context.user_data['awaiting_language_preference'] = True
        context.user_data['language_preference'] = None
        
        # Log bot response
        self.chat_logger.log_bot_response(
            user.id,
            user.username or "unknown",
            welcome_message,
            "welcome"
        )
        
        logger.info("Sent welcome message from Puneet Guruji")
        return ONBOARDING
    
    async def handle_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all onboarding messages with Puneet Guruji"""
        user = update.effective_user
        user_message = update.message.text.strip()
        logger.info(f"Onboarding message from user {user.id}: '{user_message[:50]}...'")
        
        # Log user message
        self.chat_logger.log_user_message(
            user.id,
            user.username or "unknown",
            user_message,
            "onboarding"
        )
        
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            # Get current onboarding state and details
            current_state = context.user_data.get('onboarding_state', 'start')
            birth_details = context.user_data.get('birth_details', {})
            
            logger.info(f"Current onboarding state: {current_state}")
            logger.info(f"Current birth details: {birth_details}")
            
            # Create context for Puneet Guruji
            # Quick heuristic: if we are still missing the user's name and the message looks like a name
            # (i.e., no digits, shorter than 40 chars, and mostly alphabetic), store it immediately to
            # avoid redundant name prompts.
            if ('name' not in birth_details or not birth_details.get('name')):
                if user_message and not any(ch.isdigit() for ch in user_message) and len(user_message.split()) <= 4:
                    birth_details['name'] = user_message.strip().title()
                    context.user_data['birth_details'] = birth_details
                    logger.info(f"Heuristically captured name: {birth_details['name']}")

            # In handle_onboarding, get language_preference from context.user_data
            language = context.user_data.get('language_preference', 'hindi')

            # In onboarding LLM prompt, add language instruction
            if language == 'english':
                lang_instruction = '\nRespond ONLY in English.'
            elif language == 'hindi':
                lang_instruction = '\nRespond ONLY in Hindi.'
            else:
                lang_instruction = '\nRespond in a natural Hindi-English mix.'
            puneet_guruji_context = f"""Aap Punnet Guruji hain - ek experienced Vedic astrologer jo Hindi mein baat karte hain.

Current State: {current_state}
Current Details: {birth_details}
User Message: "{user_message}"

Aapka task:
1. User se birth details collect karna (name, date, time, place)
2. Natural Hindi mein baat karna
3. Missing details ke liye politely puchna
4. Sab details mil jane ke baad consultation ke liye puchna

Required details:
- name: Full name
- birth_date: Date in YYYY-MM-DD format  
- birth_time: Time in HH:MM format (24-hour)
- birth_place: City and state/country

Agar sab details mil gaye hain, to consultation ke liye puchiye.
Agar koi detail missing hai, to politely puchiye.

Example responses:
- "Namaste! Aapka naam kya hai?"
- "Aapka janam din kya hai? (DD/MM/YYYY format mein)"
- "Aap kis time paida huye the? (HH:MM format mein)"
- "Aap kahan paida huye the? (City, State)"
- "Bahut achha! Ab aap mujhe bataiye, aap kya janna chahte hain? Shadi ke bare mein, career ke bare mein, ya koi aur guidance chahiye?"

Respond in JSON format:
{{
    "updated_details": {{"name": "value", "birth_date": "value", "birth_time": "value", "birth_place": "value"}},
    "next_state": "collecting|complete",
    "response": "Aapka natural Hindi response",
    "missing_info": ["list of missing fields"]
}}""" + lang_instruction
            
            # Get Puneet Guruji response
            logger.info("Sending request to Puneet Guruji")
            gemini_response = self.gemini_astrologer.model.generate_content(puneet_guruji_context)
            
            # Log the raw response for debugging
            logger.info(f"Raw Puneet Guruji response: {gemini_response.text[:200]}...")
            
            try:
                # Clean the response - remove markdown code blocks if present
                response_text = gemini_response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.startswith('```'):
                    response_text = response_text[3:]  # Remove ```
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                
                response_text = response_text.strip()
                logger.info(f"Cleaned response: {response_text[:200]}...")
                
                # Parse JSON response
                response_data = json.loads(response_text)
                logger.info(f"Puneet Guruji response: {response_data}")
                
                # Update birth details
                if 'updated_details' in response_data:
                    birth_details.update(response_data['updated_details'])
                    context.user_data['birth_details'] = birth_details
                    logger.info(f"Updated birth details: {birth_details}")
                
                # Update state
                next_state = response_data.get('next_state', current_state)
                context.user_data['onboarding_state'] = next_state
                logger.info(f"Updated state to: {next_state}")
                
                # Send response to user
                user_response = response_data.get('response', "Dhanyawad! Aap apna naam batayein.")
                if context.user_data.get('language_preference', 'hindi') == 'english':
                    # Optionally, translate or use English response if available
                    # For now, just reply in English if possible
                    user_response = "Thank you! Please tell me your name." if user_response == "Dhanyawad! Aap apna naam batayein." else user_response
                await update.message.reply_text(user_response)
                
                # Log bot response
                self.chat_logger.log_bot_response(
                    user.id,
                    user.username or "unknown",
                    user_response,
                    "onboarding"
                )
                
                # If onboarding is complete, move to consultation
                if next_state == 'complete':
                    logger.info("Onboarding complete, moving to consultation")
                    context.user_data['consultation_state'] = 'ready'

                    # Log system event
                    self.chat_logger.log_system_event(
                        user.id,
                        user.username or "unknown",
                        "onboarding_complete",
                        {"birth_details": birth_details}
                    )

                    # --- NEW: Immediately address pending concern if present ---
                    # Check for last user concern in conversation history
                    last_concern = None
                    conversation_history = self.context_manager.get_conversation_history(user.id, user.username or "unknown", limit=10)
                    for msg in conversation_history:
                        if msg.get("message_type") == "user":
                            last_concern = msg.get("content")
                            break
                    # If a concern/question is present, answer it directly
                    if last_concern:
                        # Use context manager to generate answer
                        # When calling context_manager.process_user_message, pass language_preference
                        response_text, context_analysis = self.context_manager.process_user_message(
                            user_message=last_concern,
                            chart_data=birth_details,
                            user_name=birth_details.get('name', 'User'),
                            user_id=user.id,
                            username=user.username or "unknown",
                            language_preference=language
                        )
                        await update.message.reply_text(response_text)
                        self.chat_logger.log_bot_response(
                            user.id,
                            user.username or "unknown",
                            response_text,
                            "consultation"
                        )
                        return CONSULTATION
                    else:
                        # If no concern, prompt for a question
                        prompt = "Dhanyavaad! Aapke janm ki saari jaankari mil gayi hai. Ab aap apna prashna puch sakte hain. (Jaise: career, paisa, shadi, health, education)"
                        await update.message.reply_text(prompt)
                        self.chat_logger.log_bot_response(
                            user.id,
                            user.username or "unknown",
                            prompt,
                            "onboarding_prompt"
                        )
                        return CONSULTATION
                    # --- END NEW ---
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing Puneet Guruji JSON response: {str(e)}")
                logger.error(f"Raw response was: {gemini_response.text}")
                
                # Fallback response
                fallback_response = """Namaste! Main aapki help karunga.

Kripya apni birth details share karein:
- Aapka naam
- Janam din (DD/MM/YYYY)
- Janam ka samay (HH:MM)
- Janam sthan (City, State)

Aap ye sab details ek saath ya ek-ek karke share kar sakte hain."""
                
                await update.message.reply_text(fallback_response)
                
                # Log bot response
                self.chat_logger.log_bot_response(
                    user.id,
                    user.username or "unknown",
                    fallback_response,
                    "onboarding_fallback"
                )
            
        except Exception as e:
            logger.error(f"Error in onboarding for user {user.id}: {str(e)}")
            error_response = "Maaf kijiye, kuch technical problem aa raha hai. Please try again."
            await update.message.reply_text(error_response)
            
            # Log error response
            self.chat_logger.log_bot_response(
                user.id,
                user.username or "unknown",
                error_response,
                "error"
            )
        
        return ONBOARDING
    
    async def handle_consultation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle consultation messages after birth details are collected"""
        user = update.effective_user
        user_message = update.message.text.strip()
        logger.info(f"Consultation message from user {user.id}: '{user_message[:50]}...'")
        
        # Log user message
        self.chat_logger.log_user_message(
            user.id,
            user.username or "unknown",
            user_message,
            "consultation"
        )
        
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            # Get birth details
            birth_details = context.user_data.get('birth_details', {})
            
            # Check if we have all required details
            required_fields = ['name', 'birth_date', 'birth_time', 'birth_place']
            missing_fields = [field for field in required_fields if field not in birth_details or not birth_details[field]]
            
            if missing_fields:
                logger.info(f"Missing birth details: {missing_fields}")
                error_response = "Maaf kijiye, abhi tak aapki complete birth details nahi mili hain. Please /start karke dobara try karein."
                await update.message.reply_text(error_response)
                
                # Log error response
                self.chat_logger.log_bot_response(
                    user.id,
                    user.username or "unknown",
                    error_response,
                    "missing_details"
                )
                
                return ConversationHandler.END
            
            # Calculate birth chart if not already done
            if 'chart_data' not in context.user_data:
                logger.info("Calculating birth chart for consultation")
                await self._calculate_and_save_chart(update, context, birth_details)
            
            # Get chart data
            chart_data = context.user_data.get('chart_data', {})
            
            # Initialize conversation memory if not exists
            if 'conversation_memory' not in context.user_data:
                context.user_data['conversation_memory'] = {
                    'asked_questions': [],
                    'last_question': None,
                    'last_category': None,
                    'session_start': datetime.now().isoformat()
                }
            
            conversation_memory = context.user_data['conversation_memory']
            
            # Determine question category
            question_lower = user_message.lower()
            category = None
            
            # Check for clarification/follow-up questions first
            clarification_keywords = ['kya keh rahe', 'kya keh rahen', 'samajh nahi aa raha', 'explain', 'clarify', 'detail', 'batao', 'bataiye']
            if any(word in question_lower for word in clarification_keywords):
                category = 'clarification'
            # Marriage keywords (including common misspellings)
            elif any(word in question_lower for word in ['shadi', 'marriage', 'vivah', 'shaadi', 'shaddi', 'marry']):
                category = 'marriage'
            elif any(word in question_lower for word in ['career', 'job', 'business', 'profession', 'naukri', 'vyapar', 'promotion', 'increment', 'salary', 'appraisal']):
                category = 'career'
            elif any(word in question_lower for word in ['health', 'swasth', 'bimar', 'illness', 'disease']):
                category = 'health'
            elif any(word in question_lower for word in ['education', 'study', 'padhai', 'exam', 'college']):
                category = 'education'
            elif any(word in question_lower for word in ['money', 'wealth', 'finance', 'paisa', 'dhan', 'income']):
                category = 'finance'
            
            logger.info(f"Question category determined: {category}")

            # --- NEW: Use context-aware response generation ---
            try:
                # In consultation handler, also pass language_preference
                user_name = birth_details.get('name', 'User')
                response_text, context_analysis = self.context_manager.process_user_message(
                    user_message=user_message,
                    chart_data=chart_data,
                    user_name=user_name,
                    user_id=user.id,
                    username=user.username or "unknown",
                    language_preference=language
                )

                # --- NEW: Handle extracted birth details ---
                extracted = context_analysis.get('extracted_birth_details', {}) if context_analysis else {}
                updated = False
                missing_fields = []
                if extracted:
                    for key in ['name', 'birth_date', 'birth_time', 'birth_place']:
                        val = extracted.get(key)
                        if val and (not birth_details.get(key) or birth_details.get(key) != val):
                            birth_details[key] = val
                            updated = True
                        if not birth_details.get(key):
                            missing_fields.append(key)
                    context.user_data['birth_details'] = birth_details

                # If we just updated or found missing details, acknowledge/confirm
                if updated or missing_fields:
                    confirm_msg = ""
                    if updated:
                        confirm_msg += "🙏 Aapke janm vivaran ko update kar diya gaya hai.\n"
                        confirm_msg += f"Naam: {birth_details.get('name', 'N/A')}\n"
                        confirm_msg += f"Janm Tithi: {birth_details.get('birth_date', 'N/A')}\n"
                        confirm_msg += f"Samay: {birth_details.get('birth_time', 'N/A')}\n"
                        confirm_msg += f"Sthan: {birth_details.get('birth_place', 'N/A')}\n"
                    if missing_fields:
                        field_map = {
                            'name': 'apna poora naam',
                            'birth_date': 'janm tithi (DD/MM/YYYY)',
                            'birth_time': 'janm samay (HH:MM, 24-hour)',
                            'birth_place': 'janm sthan (city, state/country)'
                        }
                        confirm_msg += "\nKripya in details ko poora karein: "
                        confirm_msg += ", ".join([field_map[f] for f in missing_fields])
                    await update.message.reply_text(confirm_msg)
                    self.chat_logger.log_bot_response(
                        user.id,
                        user.username or "unknown",
                        confirm_msg,
                        "birth_details_confirmation"
                    )
                    # If missing, do not proceed to main response
                    if missing_fields:
                        return CONSULTATION
                # --- END NEW ---

                await update.message.reply_text(response_text)

                # Log bot response
                self.chat_logger.log_bot_response(
                    user.id,
                    user.username or "unknown",
                    response_text,
                    "consultation"
                )

                # Log context analysis for debugging
                logger.info(f"Context analysis: {context_analysis.get('context_analysis', {}).get('question_category', 'unknown')}")

                # Update conversation memory with context analysis
                if context_analysis:
                    analysis = context_analysis.get('context_analysis', {})
                    question_category = analysis.get('question_category', category)
                    
                    if question_category and question_category not in conversation_memory['asked_questions']:
                        conversation_memory['asked_questions'].append(question_category)
                    
                    conversation_memory['last_question'] = user_message
                    conversation_memory['last_category'] = question_category
                    
                    # Store context analysis for future reference
                    context.user_data['last_context_analysis'] = context_analysis

                return CONSULTATION

            except Exception as e:
                logger.error(f"Error in context-aware response generation: {str(e)}")
                # For all static/fallback messages, select by language
                if language == 'english':
                    fallback_response = "Sorry, there was a technical problem. Please try again."
                else:
                    fallback_response = "Maaf kijiye, kuch technical problem aa raha hai. Please try again."
                await update.message.reply_text(fallback_response)
                self.chat_logger.log_bot_response(
                    user.id,
                    user.username or "unknown",
                    fallback_response,
                    "consultation_error"
                )
                return CONSULTATION

            # --- END NEW LOGIC ---
            
            # Get astrological guidance from knowledge base
            logger.info("Getting astrological guidance from knowledge base")
            astrological_guidance = self.knowledge_base.get_astrological_guidance(
                chart_data, user_message, category
            )
            
            # Create comprehensive response using Puneet Guruji style
            chart_info = f"""
📊 आपकी जन्म कुंडली के अनुसार:
• लग्न: {chart_data.get('ascendant_sign', 'Unknown')}
• सूर्य राशि: {chart_data.get('sun_sign', 'Unknown')}
• चंद्र राशि: {chart_data.get('moon_sign', 'Unknown')}
• वर्तमान दशा: {chart_data.get('dasha', {}).get('current_dasha', 'Unknown')}
"""
            
            # Create context-aware response
            if category == 'clarification':
                # Handle clarification requests
                logger.info("User asking for clarification, providing detailed explanation")
                if 'career' in conversation_memory['asked_questions']:
                    clarification_response = f"""🙏 नमस्ते! मैं आपके करियर के बारे में विस्तार से बता रहा हूं।

{chart_info}

🔮 आपके करियर के लिए विशेष मार्गदर्शन:
• सूर्य 10वें घर में है - यह सरकारी नौकरी या नेतृत्व की भूमिका दर्शाता है
• चंद्र मजबूत है - मनोविज्ञान और मेहमाननवाजी के क्षेत्र में सफलता
• आपका लग्न Scorpio है - यह शोध और गहन विश्लेषण की क्षमता दर्शाता है

💡 सलाह: आप इन क्षेत्रों में सफल हो सकते हैं:
• सरकारी सेवा या प्रशासनिक पद
• मनोविज्ञान या काउंसलिंग
• होटल मैनेजमेंट या पर्यटन
• शोध या विश्लेषणात्मक कार्य

क्या आप किसी विशेष क्षेत्र के बारे में और जानना चाहते हैं?"""
                elif 'marriage' in conversation_memory['asked_questions']:
                    clarification_response = f"""🙏 नमस्ते! मैं आपकी शादी के बारे में विस्तार से बता रहा हूं।

{chart_info}

🔮 आपकी शादी के लिए विशेष मार्गदर्शन:
• शुक्र की स्थिति शादी के लिए अनुकूल है
• चंद्र का प्रभाव जीवनसाथी के स्वभाव पर है
• सूर्य का प्रभाव शादी के समय पर है

💡 सलाह: आपकी शादी के लिए अनुकूल समय और जीवनसाथी का स्वभाव कैसा होगा, यह जानना चाहते हैं?"""
                else:
                    clarification_response = f"""🙏 नमस्ते! मैं आपकी जन्म कुंडली के आधार पर मार्गदर्शन दे रहा हूं।

{chart_info}

🔮 ज्योतिषीय मार्गदर्शन:
{astrological_guidance}

💡 क्या आप किसी विशेष क्षेत्र के बारे में जानना चाहते हैं?
• 💑 शादी और रिश्ते
• 💼 करियर और व्यवसाय  
• 🏥 स्वास्थ्य और कल्याण
• 📚 शिक्षा और ज्ञान
• 💰 धन और समृद्धि"""
                
                puneet_response = clarification_response
            elif is_repeat_question:
                # If repeat question, acknowledge and provide additional guidance
                repeat_response = f"""🙏 नमस्ते! मैं देख रहा हूं कि आपने पहले भी {self._get_category_name_hindi(category)} के बारे में पूछा था।

{chart_info}

🔮 अतिरिक्त ज्योतिषीय मार्गदर्शन:
{astrological_guidance}

💡 क्या आप किसी अन्य क्षेत्र के बारे में जानना चाहते हैं?
• 💑 शादी और रिश्ते
• 💼 करियर और व्यवसाय  
• 🏥 स्वास्थ्य और कल्याण
• 📚 शिक्षा और ज्ञान
• 💰 धन और समृद्धि"""
                
                puneet_response = repeat_response
            else:
                # First time question, provide comprehensive guidance
                puneet_response = f"""🙏 नमस्ते! मैं आपकी जन्म कुंडली का विश्लेषण करके आपको मार्गदर्शन दे रहा हूं।

{chart_info}

🔮 ज्योतिषीय मार्गदर्शन:
{astrological_guidance}

💡 सलाह: आप अपने जीवन के किसी विशेष क्षेत्र के बारे में पूछ सकते हैं:
• 💑 शादी और रिश्ते
• 💼 करियर और व्यवसाय  
• 🏥 स्वास्थ्य और कल्याण
• 📚 शिक्षा और ज्ञान
• 💰 धन और समृद्धि

क्या आप किसी विशेष क्षेत्र के बारे में जानना चाहते हैं?"""
            
            await update.message.reply_text(puneet_response)
            
            # Log bot response
            self.chat_logger.log_bot_response(
                user.id,
                user.username or "unknown",
                puneet_response,
                "consultation"
            )
            
            # Log conversation memory update
            self.chat_logger.log_system_event(
                user.id,
                user.username or "unknown",
                "conversation_memory_updated",
                {
                    "asked_questions": conversation_memory['asked_questions'],
                    "current_category": category,
                    "is_repeat": is_repeat_question
                }
            )
            
            logger.info(f"Astrological consultation response sent to user {user.id}")
            logger.info(f"Conversation memory: {conversation_memory['asked_questions']}")
            
            # Save consultation to database
            db = next(get_db())
            user_db = db.query(User).filter_by(
                telegram_id=str(user.id)
            ).first()
            
            if user_db:
                consultation = Consultation(
                    user_id=user_db.id,
                    question_type=category or 'general',
                    question=user_message,
                    prediction=puneet_response
                )
                db.add(consultation)
                db.commit()
                logger.info("Consultation saved to database")
            db.close()
            
        except Exception as e:
            logger.error(f"Error in consultation for user {user.id}: {str(e)}")
            error_response = "Maaf kijiye, kuch technical problem aa raha hai. Please try again."
            await update.message.reply_text(error_response)
            
            # Log error response
            self.chat_logger.log_bot_response(
                user.id,
                user.username or "unknown",
                error_response,
                "error"
            )
        
        return CONSULTATION
    
    async def _calculate_and_save_chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE, birth_details: dict):
        """Calculate birth chart and save to database"""
        user = update.effective_user
        logger.info(f"Calculating birth chart for user {user.id}")
        
        # Log system event
        self.chat_logger.log_system_event(
            user.id,
            user.username or "unknown",
            "chart_calculation_started",
            {"birth_details": birth_details}
        )
        
        try:
            # Parse birth details
            name = birth_details.get('name', 'Unknown')
            birth_date_str = birth_details.get('birth_date', '')
            birth_time_str = birth_details.get('birth_time', '')
            birth_place = birth_details.get('birth_place', '')
            
            # Convert date and time
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            birth_time = datetime.strptime(birth_time_str, "%H:%M").time()
            
            logger.info(f"Parsed details - Date: {birth_date}, Time: {birth_time}, Place: {birth_place}")
            
            # Calculate birth chart
            chart_data = self.calculator.generate_birth_chart(
                name, birth_date, birth_time, birth_place
            )
            logger.info(f"Birth chart calculated successfully for {name}")
            
            # Save chart data to context
            context.user_data['chart_data'] = chart_data
            
            # Save to database
            logger.info("Saving user data to database")
            db = next(get_db())
            user_db = db.query(User).filter_by(
                telegram_id=str(user.id)
            ).first()
            
            if not user_db:
                logger.info(f"Creating new user record for {user.id}")
                user_db = User(telegram_id=str(user.id))
                db.add(user_db)
            
            user_db.name = name
            user_db.birth_date = datetime.combine(birth_date, datetime.min.time())
            user_db.birth_time = datetime.combine(datetime.min.date(), birth_time)
            user_db.birth_place = birth_place
            user_db.latitude = chart_data['coordinates']['latitude']
            user_db.longitude = chart_data['coordinates']['longitude']
            user_db.timezone = chart_data['timezone']
            user_db.chart_data = json.dumps(chart_data)
            user_db.onboarding_complete = True
            
            db.commit()
            logger.info(f"User data saved successfully for {user.id}")
            db.close()
            
            # Do NOT send any static success message here. The onboarding/consultation handler will handle the next step.
            return
            
        except Exception as e:
            logger.error(f"Error calculating chart for user {user.id}: {str(e)}")
            error_response = f"Maaf kijiye, aapka janam kundli calculate karne mein problem aa raha hai: {str(e)}. Please try again."
            await update.message.reply_text(error_response)
            
            # Log error response
            self.chat_logger.log_bot_response(
                user.id,
                user.username or "unknown",
                error_response,
                "chart_calculation_error"
            )
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation"""
        user = update.effective_user
        logger.info(f"Cancel command received from user {user.id}")
        
        # Log user command
        self.chat_logger.log_user_message(
            user.id,
            user.username or "unknown",
            "/cancel",
            "command"
        )
        
        language = context.user_data.get('language_preference', 'hindi')
        if language == 'english':
            cancel_message = 'Okay, the operation has been cancelled. You can /start to begin again. 🙏'
        else:
            cancel_message = 'Theek hai Beta, operation cancel kar diya gaya hai. Aap /start karke dobara shuru kar sakte hain. 🙏'
        await update.message.reply_text(
            cancel_message,
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Log bot response
        self.chat_logger.log_bot_response(
            user.id,
            user.username or "unknown",
            cancel_message,
            "cancel"
        )
        
        return ConversationHandler.END
    
    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show conversation history"""
        user = update.effective_user
        logger.info(f"History command received from user {user.id}")
        
        # Log user command
        self.chat_logger.log_user_message(
            user.id,
            user.username or "unknown",
            "/history",
            "command"
        )
        
        language = context.user_data.get('language_preference', 'hindi')
        conversation_memory = context.user_data.get('conversation_memory', {})
        asked_questions = conversation_memory.get('asked_questions', [])
        
        if not asked_questions:
            if language == 'english':
                history_message = "📋 Your conversation history:\n\nNo questions have been asked yet.\n\nYou can ask about the following areas:\n• 💑 Marriage & Relationships\n• 💼 Career & Business\n• 🏥 Health & Wellness\n• 📚 Education & Knowledge\n• 💰 Wealth & Prosperity"
            else:
                history_message = "📋 आपकी बातचीत का इतिहास:\n\nकोई प्रश्न अभी तक नहीं पूछा गया है।\n\nआप निम्नलिखित क्षेत्रों के बारे में पूछ सकते हैं:\n• 💑 शादी और रिश्ते\n• 💼 करियर और व्यवसाय  \n• 🏥 स्वास्थ्य और कल्याण\n• 📚 शिक्षा और ज्ञान\n• 💰 धन और समृद्धि"
        else:
            if language == 'english':
                question_names = [q.capitalize() for q in asked_questions]
                history_message = f"📋 Your conversation history:\n\nQuestions asked:\n{chr(10).join([f'• {name}' for name in question_names])}\n\n💡 You can ask more about these areas:\n• 💑 Marriage & Relationships\n• 💼 Career & Business\n• 🏥 Health & Wellness\n• 📚 Education & Knowledge\n• 💰 Wealth & Prosperity"
            else:
                question_names = [self._get_category_name_hindi(q) for q in asked_questions]
                history_message = f"📋 आपकी बातचीत का इतिहास:\n\nपूछे गए प्रश्न:\n{chr(10).join([f'• {name}' for name in question_names])}\n\n💡 आप इन क्षेत्रों के बारे में और जानकारी प्राप्त कर सकते हैं:\n• 💑 शादी और रिश्ते\n• 💼 करियर और व्यवसाय  \n• 🏥 स्वास्थ्य और कल्याण\n• 📚 शिक्षा और ज्ञान\n• 💰 धन और समृद्धि"
        await update.message.reply_text(history_message)
        self.chat_logger.log_bot_response(
            user.id,
            user.username or "unknown",
            history_message,
            "history"
        )
        return CONSULTATION
    
    async def reset_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset conversation memory"""
        user = update.effective_user
        logger.info(f"Reset memory command received from user {user.id}")
        
        # Log user command
        self.chat_logger.log_user_message(
            user.id,
            user.username or "unknown",
            "/reset",
            "command"
        )
        
        language = context.user_data.get('language_preference', 'hindi')
        # Reset conversation memory
        if 'conversation_memory' in context.user_data:
            context.user_data['conversation_memory'] = {
                'asked_questions': [],
                'last_question': None,
                'last_category': None,
                'session_start': datetime.now().isoformat()
            }
        if language == 'english':
            reset_message = "🔄 Conversation history has been reset.\n\nYou can now ask all questions again:\n• 💑 Marriage & Relationships\n• 💼 Career & Business\n• 🏥 Health & Wellness\n• 📚 Education & Knowledge\n• 💰 Wealth & Prosperity"
        else:
            reset_message = "🔄 बातचीत का इतिहास रीसेट कर दिया गया है।\n\nअब आप सभी प्रश्न फिर से पूछ सकते हैं:\n• 💑 शादी और रिश्ते\n• 💼 करियर और व्यवसाय  \n• 🏥 स्वास्थ्य और कल्याण\n• 📚 शिक्षा और ज्ञान\n• 💰 धन और समृद्धि"
        await update.message.reply_text(reset_message)
        self.chat_logger.log_bot_response(
            user.id,
            user.username or "unknown",
            reset_message,
            "reset"
        )
        self.chat_logger.log_system_event(
            user.id,
            user.username or "unknown",
            "conversation_memory_reset",
            {"reset_time": datetime.now().isoformat()}
        )
        return CONSULTATION

    def _get_category_name_hindi(self, category):
        """Get Hindi name for category"""
        category_names = {
            'marriage': 'शादी',
            'career': 'करियर',
            'health': 'स्वास्थ्य',
            'education': 'शिक्षा',
            'finance': 'धन'
        }
        return category_names.get(category, category)

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates"""
    logger.error(f'Update "{update}" caused error "{context.error}"')
    if update and update.effective_user:
        logger.error(f"Error for user {update.effective_user.id}: {context.error}") 
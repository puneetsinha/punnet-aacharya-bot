# Punnet Aacharya - Vedic Astrology Telegram Bot

A comprehensive Python implementation for a Vedic Astrology Telegram bot that provides marriage timing and career guidance predictions using **Gemini Flash 2.0** for intelligent context detection and natural responses.

## Features

- **🤖 Intelligent Context Detection**: Gemini AI automatically detects whether questions are about marriage, career, or general life guidance
- **🗣️ Natural Hindi Astrologer Responses**: Responds like a real Hindi astrologer with warm, spiritual language
- **🔮 Complete Birth Chart Calculation**: Uses Swiss Ephemeris for accurate planetary positions
- **💑 Marriage Timing Predictions**: Analyzes 7th house, Venus, Jupiter positions and D9 chart
- **💼 Career Guidance**: Based on 10th house, planetary positions and D10 chart
- **🌙 Dasha Period Analysis**: Vimshottari Dasha calculations
- **🧠 Vector Database Integration**: ChromaDB for storing astrological knowledge
- **💾 Persistent Storage**: SQLAlchemy database for user data and consultations
- **📊 Comprehensive Logging**: Detailed logging system for debugging and monitoring

## Project Structure

```
punnet_aacharya/
│
├── main.py                 # Main bot entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── database.py           # Database models and operations
├── vector_store.py       # Vector database for knowledge
├── astro_calculator.py   # Core astrological calculations
├── gemini_service.py     # Gemini AI integration
├── bot_handlers.py       # Telegram bot handlers
├── prompts.py           # Bot conversation prompts
├── log_viewer.py        # Log monitoring utility
├── env.example          # Environment variables template
├── logs/                # Log files directory
└── knowledge/           # Astrology knowledge base
    ├── marriage_rules.json
    └── career_rules.json
```

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd punnet_aacharya

# Activate virtual environment
source Puneetaacharya/bin/activate

# Install dependencies (already done)
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy environment template
cp env.example .env

# Edit .env file and add your API keys
```

### 3. Get API Keys

#### Telegram Bot Token:
1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token

#### Gemini API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 4. Run the Bot

```bash
# Make sure virtual environment is activated
source Puneetaacharya/bin/activate

# Run the bot
python main.py
```

---

### Running with Docker

```bash
# Build the Docker image
docker build -t punnet-aacharya-bot .

# Run the bot (make sure to provide your .env file for secrets)
docker run --env-file .env punnet-aacharya-bot
```

- Ensure your `.env` file is in the project root and contains your API keys.
- The container will run the bot in polling mode (no ports need to be exposed).

## Logging System

The bot includes a comprehensive logging system that tracks all operations, calculations, and user interactions.

### Log Files

Logs are stored in the `logs/` directory with the format:
```
logs/punnet_aacharya_YYYYMMDD.log
```

### Log Levels

- **INFO**: General operations, user interactions, successful calculations
- **DEBUG**: Detailed calculation steps, function calls, data processing
- **WARNING**: Non-critical issues, validation failures
- **ERROR**: Critical errors, exceptions, failures

### Log Format

```
2024-01-15 10:30:45,123 - module_name - INFO - function_name:123 - Message
```

### Using the Log Viewer

The `log_viewer.py` utility helps monitor and analyze logs:

```bash
# View recent logs
python log_viewer.py view

# Follow logs in real-time
python log_viewer.py follow

# Analyze log statistics
python log_viewer.py analyze

# Filter by log level
python log_viewer.py view --level=ERROR

# Filter by function
python log_viewer.py view --function=generate_birth_chart

# Get help
python log_viewer.py help
```

### What Gets Logged

#### Astrological Calculations
- Birth chart generation steps
- Planetary position calculations
- House calculations
- Dasha period calculations
- Divisional chart calculations

#### User Interactions
- User messages and commands
- Onboarding process steps
- Chart calculation requests
- Gemini AI interactions

#### System Operations
- Database operations
- Vector database queries
- API calls and responses
- Error handling and recovery

#### Performance Metrics
- Response times for Gemini AI
- Calculation durations
- Database query performance
- Memory usage patterns

### Debugging with Logs

#### Common Issues and Log Patterns

1. **Chart Calculation Failures**:
   ```
   ERROR - Error calculating birth chart: Could not find coordinates for {place}
   ```

2. **Gemini AI Issues**:
   ```
   ERROR - Error getting response from Gemini: API key invalid
   ```

3. **Database Problems**:
   ```
   ERROR - Error in database session: Connection timeout
   ```

4. **User Input Validation**:
   ```
   WARNING - Invalid date format from user 123456: '15/13/1990'
   ```

#### Performance Monitoring

Monitor these key metrics:
- Gemini AI response times
- Chart calculation duration
- Database operation frequency
- User interaction patterns

## How It Works

### 🤖 Intelligent Conversation Flow

1. **Start with `/start`** - User provides birth details
2. **Natural Questions** - Users can ask anything naturally:
   - "Meri shadi kab hogi?" (When will I get married?)
   - "Career mein kya karna chahiye?" (What should I do in career?)
   - "Mera future kaisa hai?" (How is my future?)
   - "Dasha periods ke bare mein batao" (Tell me about dasha periods)

3. **Gemini AI Analysis** - The bot automatically:
   - Detects the context of the question
   - Analyzes the birth chart data
   - Provides personalized responses in Hindi astrologer style

### 🗣️ Natural Hindi Astrologer Personality

The bot responds like a real Hindi astrologer with:
- Warm and spiritual language
- Mix of Hindi and English naturally
- Respectful addressing ("Aap", "Beta", "Putra/Putri")
- Spiritual phrases and blessings
- Practical advice with astrological reasoning

## Bot Commands

- `/start` - Begin the onboarding process
- `/cancel` - Cancel current conversation

**No specific commands needed!** Just ask naturally:
- "Shadi ke bare mein batao"
- "Career guidance chahiye"
- "Mera kundli kaisa hai?"
- "Dasha periods ke bare mein puchna tha"

## Astrological Features

### Birth Chart Calculation
- Uses Swiss Ephemeris for precise planetary positions
- Calculates Lahiri Ayanamsa for Vedic positions
- Generates divisional charts (D9 for marriage, D10 for career)
- Calculates Vimshottari Dasha periods

### Marriage Analysis
- 7th house analysis
- Venus and Jupiter positions
- Navamsa (D9) chart analysis
- Dasha period timing
- Age-specific predictions

### Career Analysis
- 10th house and lord analysis
- Dasamsa (D10) chart
- Planet-based career recommendations
- Growth period predictions

## Dependencies

- `python-telegram-bot==20.7` - Telegram bot framework
- `google-generativeai==0.8.5` - Gemini AI integration
- `pyswisseph==2.10.3.2` - Swiss Ephemeris for astronomical calculations
- `chromadb==0.4.22` - Vector database for knowledge storage
- `sqlalchemy==2.0.25` - Database ORM
- `geopy==2.4.1` - Geocoding for place coordinates
- `timezonefinder==6.4.0` - Timezone detection

## Usage Examples

### Marriage Questions:
- "Meri shadi kab hogi?"
- "Love marriage ya arranged marriage?"
- "Partner kaise milega?"
- "Shadi mein delay kyun aa raha hai?"

### Career Questions:
- "Career mein kya karna chahiye?"
- "Business karna chahiye ya job?"
- "Job change kab karna chahiye?"
- "Success kab milegi?"

### General Questions:
- "Mera future kaisa hai?"
- "Koi problem hai kya?"
- "Remedies batao"
- "Dasha periods ke bare mein batao"

## Troubleshooting

### Common Issues

1. **Bot not responding**: Check logs for API key issues
2. **Chart calculation errors**: Verify place names and coordinates
3. **Gemini AI failures**: Check API key and network connectivity
4. **Database errors**: Verify SQLite file permissions

### Log Analysis Commands

```bash
# Check for errors
python log_viewer.py view --level=ERROR

# Monitor user interactions
python log_viewer.py view --function=handle_message

# Track chart calculations
python log_viewer.py view --function=generate_birth_chart

# Real-time monitoring
python log_viewer.py follow
```

## Notes

- The bot requires complete birth details for accurate predictions
- All calculations are based on Vedic astrology principles
- User data is stored securely in the database
- The bot provides general guidance and should not replace professional consultation
- Gemini AI provides natural, conversational responses like a real astrologer
- Comprehensive logging helps with debugging and performance monitoring

## License

This project is for educational and personal use only. 
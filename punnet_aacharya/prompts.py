class BotPrompts:
    WELCOME = """🙏 Namaste! I am {bot_name}, your personal Vedic astrology guide.

I can help you understand:
🔮 When you might get married
💼 What career path suits you best

But first, I need your complete birth details to create your birth chart.

Please share your name to begin. 📿"""

    ASK_NAME = "What is your full name? 🙏"
    
    ASK_BIRTH_DATE = """Thank you, {name}! 🌟

Now, please share your date of birth.
Format: DD/MM/YYYY (e.g., 15/08/1990)"""

    ASK_BIRTH_TIME = """Perfect! 📅

Your birth time is crucial for accurate predictions.
Please share your exact birth time.
Format: HH:MM AM/PM (e.g., 10:30 AM)

If you don't know the exact time, please provide an approximate time."""

    ASK_BIRTH_PLACE = """Excellent! ⏰

Finally, I need your birth place for calculating planetary positions.
Please share your city and country of birth.
Example: Mumbai, India"""

    INCOMPLETE_DETAILS = """🚫 I notice you haven't provided all the required details yet.

For accurate astrological predictions, I need:
✅ Your name: {has_name}
✅ Date of birth: {has_date}
✅ Time of birth: {has_time}
✅ Place of birth: {has_place}

Without complete information, I cannot calculate your birth chart and provide accurate predictions about marriage or career.

Please provide the missing details."""

    CHART_CALCULATED = """🎉 Wonderful! I have successfully calculated your birth chart.

📊 Your Birth Details:
Name: {name}
Date: {date}
Time: {time}
Place: {place}
Ascendant: {ascendant}

Your chart has been saved. You can now ask me questions about:
💑 Marriage timing and compatibility
💼 Career guidance and suitable professions

What would you like to know?"""

    CHOOSE_QUESTION = """Please choose what you'd like to know:

1️⃣ /marriage - When will I get married?
2️⃣ /career - What career is best for me?
3️⃣ /chart - Show my birth chart details
4️⃣ /dasha - Show current planetary periods"""

    ERROR_DATE_FORMAT = "❌ Invalid date format. Please use DD/MM/YYYY (e.g., 15/08/1990)"
    
    ERROR_TIME_FORMAT = "❌ Invalid time format. Please use HH:MM AM/PM (e.g., 10:30 AM)"
    
    ERROR_PLACE_NOT_FOUND = "❌ Could not find coordinates for '{place}'. Please provide a valid city name with country." 
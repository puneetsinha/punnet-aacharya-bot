class BotPrompts:
    # Hindi and English versions for each prompt
    WELCOME_HI = "🙏 Namaste! Main hoon {bot_name}, aapka vyaktigat Vedic astrology guide.\n\nMain aapki madad kar sakta hoon:\n🔮 Kab shaadi hogi\n💼 Kaunsa career aapke liye sahi hai\n\nLekin sabse pehle, mujhe aapki poori janm jaankari chahiye.\n\nKripya apna naam batayein. 📿"
    WELCOME_EN = "🙏 Namaste! I am {bot_name}, your personal Vedic astrology guide.\n\nI can help you with:\n🔮 When you might get married\n💼 What career path suits you best\n\nBut first, I need your complete birth details.\n\nPlease share your name to begin. 📿"

    ASK_NAME_HI = "Aapka poora naam kya hai? 🙏"
    ASK_NAME_EN = "What is your full name? 🙏"
    
    ASK_BIRTH_DATE_HI = "Dhanyavaad, {name}! 🌟\n\nAb apni janm tithi batayein.\nFormat: DD/MM/YYYY (jaise: 15/08/1990)"
    ASK_BIRTH_DATE_EN = "Thank you, {name}! 🌟\n\nNow, please share your date of birth.\nFormat: DD/MM/YYYY (e.g., 15/08/1990)"

    ASK_BIRTH_TIME_HI = "Bahut accha! 📅\n\nAapka janm samay sahi prediction ke liye zaroori hai.\nKripya apna exact janm samay batayein.\nFormat: HH:MM (24-hour, jaise: 10:30)"
    ASK_BIRTH_TIME_EN = "Perfect! 📅\n\nYour birth time is crucial for accurate predictions.\nPlease share your exact birth time.\nFormat: HH:MM (24-hour, e.g., 10:30)"

    ASK_BIRTH_PLACE_HI = "Shandar! ⏰\n\nAkhri mein, mujhe aapka janm sthan chahiye.\nKripya apna shehar aur desh batayein.\nUdaharan: Mumbai, India"
    ASK_BIRTH_PLACE_EN = "Excellent! ⏰\n\nFinally, I need your birth place.\nPlease share your city and country of birth.\nExample: Mumbai, India"

    INCOMPLETE_DETAILS_HI = "🚫 Lagta hai aapne abhi tak saari details nahi di hain.\n\nSahi prediction ke liye mujhe chahiye:\n✅ Naam: {has_name}\n✅ Janm tithi: {has_date}\n✅ Janm samay: {has_time}\n✅ Janm sthan: {has_place}\n\nBina poori jaankari ke, main sahi prediction nahi de sakta.\n\nKripya missing details dein."
    INCOMPLETE_DETAILS_EN = "🚫 I notice you haven't provided all the required details yet.\n\nFor accurate astrological predictions, I need:\n✅ Your name: {has_name}\n✅ Date of birth: {has_date}\n✅ Time of birth: {has_time}\n✅ Place of birth: {has_place}\n\nWithout complete information, I cannot calculate your birth chart and provide accurate predictions about marriage or career.\n\nPlease provide the missing details."

    CHART_CALCULATED_HI = "🎉 Shandar! Maine aapki janm kundli bana li hai.\n\n📊 Janm Vivaran:\nNaam: {name}\nTithi: {date}\nSamay: {time}\nSthan: {place}\nAscendant: {ascendant}\n\nAb aap mujhse shaadi, career, ya kisi bhi vishay par sawal pooch sakte hain."
    CHART_CALCULATED_EN = "🎉 Wonderful! I have successfully calculated your birth chart.\n\n📊 Your Birth Details:\nName: {name}\nDate: {date}\nTime: {time}\nPlace: {place}\nAscendant: {ascendant}\n\nYou can now ask me questions about marriage, career, or any other topic."

    CHOOSE_QUESTION_HI = "Kripya batayein, aap kya janna chahenge:\n1️⃣ /marriage - Shaadi kab hogi?\n2️⃣ /career - Kaunsa career sahi hai?\n3️⃣ /chart - Janm kundli dekhein\n4️⃣ /dasha - Vartaman dasha dekhein"
    CHOOSE_QUESTION_EN = "Please choose what you'd like to know:\n1️⃣ /marriage - When will I get married?\n2️⃣ /career - What career is best for me?\n3️⃣ /chart - Show my birth chart details\n4️⃣ /dasha - Show current planetary periods"

    ERROR_DATE_FORMAT = "❌ Invalid date format. Please use DD/MM/YYYY (e.g., 15/08/1990)"
    
    ERROR_TIME_FORMAT = "❌ Invalid time format. Please use HH:MM AM/PM (e.g., 10:30 AM)"
    
    ERROR_PLACE_NOT_FOUND = "❌ Could not find coordinates for '{place}'. Please provide a valid city name with country." 

    @staticmethod
    def get_prompt(key, language):
        """Return the correct prompt version based on language ('hindi' or 'english')."""
        suffix = '_HI' if language == 'hindi' else '_EN'
        return getattr(BotPrompts, key + suffix)

# NOTE: Use dynamic LLM-based responses wherever possible. These static prompts are for fallback or very short system messages only. 
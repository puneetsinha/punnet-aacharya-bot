#!/usr/bin/env python3
"""
Test script to verify conversation fixes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'punnet_aacharya'))

from gemini_service import GeminiAstrologer
import json

def test_gemini_responses():
    """Test Gemini responses to ensure they are human-like and within limits"""
    
    print("Testing Gemini Astrologer responses...")
    
    try:
        gemini = GeminiAstrologer()
        print("✅ GeminiAstrologer initialized successfully")
        
        # Test chart data
        test_chart = {
            "name": "Shalini Arora",
            "birth_date": "1992-08-14",
            "birth_time": "10:30",
            "birth_place": "Delhi, India",
            "ascendant": "Libra",
            "planets": {
                "Sun": {"sign": "Leo", "house": 5},
                "Moon": {"sign": "Pisces", "house": 12},
                "Mars": {"sign": "Cancer", "house": 4},
                "Mercury": {"sign": "Virgo", "house": 6},
                "Jupiter": {"sign": "Libra", "house": 1},
                "Venus": {"sign": "Leo", "house": 5},
                "Saturn": {"sign": "Aquarius", "house": 11}
            },
            "houses": {
                "cusps": [202.03, 232.03, 262.03, 292.03, 322.03, 352.03, 22.03, 52.03, 82.03, 112.03, 142.03, 172.03]
            },
            "dasha": {
                "current_dasha": "Mars"
            }
        }
        
        # Test career prediction
        print("\n🔮 Testing Career Prediction...")
        career_response = gemini.generate_career_prediction(json.dumps(test_chart), "Shalini Arora")
        print(f"Career response length: {len(career_response)} characters")
        print(f"Response preview: {career_response[:200]}...")
        
        if len(career_response) > 3000:
            print("❌ Career response too long!")
        else:
            print("✅ Career response within limits")
        
        # Test marriage prediction
        print("\n💑 Testing Marriage Prediction...")
        marriage_response = gemini.generate_marriage_prediction(json.dumps(test_chart), "Shalini Arora")
        print(f"Marriage response length: {len(marriage_response)} characters")
        print(f"Response preview: {marriage_response[:200]}...")
        
        if len(marriage_response) > 3000:
            print("❌ Marriage response too long!")
        else:
            print("✅ Marriage response within limits")
        
        # Test general context detection
        print("\n🤖 Testing Context Detection...")
        general_response = gemini.detect_context_and_respond("career ke bare mein bataiye", json.dumps(test_chart), "Shalini Arora")
        print(f"General response length: {len(general_response)} characters")
        print(f"Response preview: {general_response[:200]}...")
        
        if len(general_response) > 3000:
            print("❌ General response too long!")
        else:
            print("✅ General response within limits")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    test_gemini_responses() 
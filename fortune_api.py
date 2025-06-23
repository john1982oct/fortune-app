
from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Load birthday profile data
with open("birthdays_full.json", "r", encoding="utf-8") as f:
    birthday_profiles = json.load(f)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

# Zodiac sign determination
def get_zodiac_sign(month, day):
    zodiac_dates = [
        ((1, 20), (2, 18), "Aquarius"),
        ((2, 19), (3, 20), "Pisces"),
        ((3, 21), (4, 19), "Aries"),
        ((4, 20), (5, 20), "Taurus"),
        ((5, 21), (6, 20), "Gemini"),
        ((6, 21), (7, 22), "Cancer"),
        ((7, 23), (8, 22), "Leo"),
        ((8, 23), (9, 22), "Virgo"),
        ((9, 23), (10, 22), "Libra"),
        ((10, 23), (11, 21), "Scorpio"),
        ((11, 22), (12, 21), "Sagittarius"),
        ((12, 22), (1, 19), "Capricorn")
    ]
    for start, end, sign in zodiac_dates:
        if (month == start[0] and day >= start[1]) or (month == end[0] and day <= end[1]):
            return sign
    return "Capricorn"

# Life Path descriptions
life_path_meanings = {
    1: "Leader and pioneer. You are independent, driven, and full of fresh ideas.",
    2: "Peacemaker and partner. You bring balance, diplomacy, and emotional intelligence.",
    3: "Creative communicator. You inspire through words, art, and joyful energy.",
    4: "Builder and stabilizer. You value structure, hard work, and trustworthiness.",
    5: "Adventurer and freedom seeker. You thrive on change, travel, and excitement.",
    6: "Nurturer and healer. You protect those you love and create harmony at home.",
    7: "Thinker and seeker. You are introspective, intuitive, and spiritually aware.",
    8: "Ambitious powerhouse. You’re destined for success, leadership, and wealth.",
    9: "Humanitarian and dreamer. You uplift others with your wisdom and compassion.",
    11: "Spiritual illuminator. You are highly intuitive and meant to inspire masses.",
    22: "Master builder. You turn big dreams into real-world legacies.",
    33: "Compassionate teacher. You lead through unconditional love and service."
}

# Numerology lucky number calculator
def calculate_lucky_numbers(birthdate_obj):
    digits = [int(d) for d in birthdate_obj.strftime("%Y%m%d")]
    life_path = sum(digits)
    while life_path > 9 and life_path not in [11, 22, 33]:
        life_path = sum([int(d) for d in str(life_path)])

    day = birthdate_obj.day
    month = birthdate_obj.month

    num1 = life_path + day
    num2 = life_path + month
    num3 = life_path * 3
    num4 = life_path * life_path

    all_nums = list(set([
        life_path,
        day,
        month,
        num1 % 100,
        num2 % 100,
        num3 % 100,
        num4 % 100,
    ]))

    final_nums = sorted([n for n in all_nums if 1 <= n <= 49])[:6]

    return {
        "lucky_numbers": final_nums,
        "life_path": life_path,
        "life_path_meaning": life_path_meanings.get(life_path, "A unique force with uncommon traits.")
    }

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/fortune", methods=["POST"])
def generate_fortune():
    data = request.get_json()
    dob = data.get("dob")
    time = data.get("time")
    gender = data.get("gender")

    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    date_key = dob_date.strftime("%m-%d")
    month = dob_date.month
    day = dob_date.day

    zodiac_sign = get_zodiac_sign(month, day)
    personality_map = {
        "Aries": "Bold and full of energy.",
        "Taurus": "Grounded and loyal.",
        "Gemini": "Curious and quick-witted.",
        "Cancer": "Sensitive and nurturing.",
        "Leo": "Confident and charismatic.",
        "Virgo": "Practical and detail-oriented.",
        "Libra": "Balanced and social.",
        "Scorpio": "Passionate and intuitive.",
        "Sagittarius": "Adventurous and optimistic.",
        "Capricorn": "Disciplined and responsible.",
        "Aquarius": "Innovative and independent.",
        "Pisces": "Compassionate and artistic."
    }
    personality = personality_map.get(zodiac_sign, "Unique and undefined.")

    lucky_day = (dob_date.replace(year=datetime.now().year) + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
    lucky_score = random.randint(70, 99)
    lucky_result = calculate_lucky_numbers(dob_date)

    lucky_numbers = lucky_result["lucky_numbers"]
    life_path = lucky_result["life_path"]
    life_path_meaning = lucky_result["life_path_meaning"]

    profile = birthday_profiles.get(date_key, {})

    return jsonify({
        "zodiac": zodiac_sign,
        "personality": personality,
        "lucky_day": lucky_day,
        "score": lucky_score,
        "lucky_numbers": lucky_numbers,
        "life_path": life_path,
        "life_path_meaning": life_path_meaning,
        "character": profile.get("character", ""),
        "character_advice": profile.get("character_advice", ""),
        "love": profile.get("love", ""),
        "love_advice": profile.get("love_advice", ""),
        "quote": profile.get("quote", ""),
        "wealth": profile.get("wealth", ""),
        "wealth_advice": profile.get("wealth_advice", ""),
        "mindset": profile.get("mindset", ""),
        "mindset_tip": profile.get("mindset_tip", ""),
        "emotion": profile.get("emotion", ""),
        "emotion_advice": profile.get("emotion_advice", ""),
        "habits": profile.get("habits", ""),
        "habits_insight": profile.get("habits_insight", ""),
        "creativity": profile.get("creativity", ""),
        "creativity_advice": profile.get("creativity_advice", "")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

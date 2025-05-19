from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime, timedelta

import random

app = Flask(__name__)

# Load birthday profile data
with open("birthdays_full.json", "r", encoding="utf-8") as f:
    birthday_profiles = json.load(f)

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

    # Dummy personality from zodiac
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

    # Lucky number and day generation logic
    lucky_day = (dob_date.replace(year=datetime.now().year) + 
                 timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
    lucky_score = random.randint(10, 99)
    lucky_numbers = sorted(random.sample(range(1, 50), 6))

    # Get birthday-specific profile
    profile = birthday_profiles.get(date_key, {
        "character": "Mysterious soul on a journey.",
        "love": "Passion hidden behind a gentle smile.",
        "quote": "The stars await your spark."
    })

    return jsonify({
        "zodiac": zodiac_sign,
        "personality": personality,
        "lucky_day": lucky_day,
        "score": lucky_score,
        "lucky_numbers": lucky_numbers,
        "character": profile["character"],
        "love": profile["love"],
        "quote": profile["quote"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, request, jsonify, render_template
import json, os, random
from datetime import datetime
from openai import OpenAI
import os
from flask_cors import CORS

# Do NOT pass proxies or anything else
client = OpenAI()  # reads OPENAI_API_KEY from the environment automatically

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")
    
# 🌟 Load birthday data
try:
    with open("birthdays_full.json", "r", encoding="utf-8") as f:
        birthday_profiles = json.load(f)
except Exception as e:
    birthday_profiles = {}
    print("⚠️ Failed to load birthdays:", e)

# 🌟 Zi Wei pattern loader
def load_ziwei_pattern(filename="ziwei_zai_wu.json"):
    path = os.path.join("ziwei_patterns", filename)
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

@app.route("/ziwei_test")
def ziwei_test():
    try:
        pattern = load_ziwei_pattern()
        return app.response_class(
            response=json.dumps(pattern, ensure_ascii=False, indent=2),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/minggong")
def get_ming_gong():
    def get_hour_branch(hour):
        hour = hour % 24  # Ensure valid hour from 0–23
        hour_ranges = [
            ((23, 0), '子'), ((1, 2), '丑'), ((3, 4), '寅'), ((5, 6), '卯'),
            ((7, 8), '辰'), ((9, 10), '巳'), ((11, 12), '午'), ((13, 14), '未'),
            ((15, 16), '申'), ((17, 18), '酉'), ((19, 20), '戌'), ((21, 22), '亥')
        ]

        for (start, end), branch in hour_ranges:
            if start < end:
                if start <= hour <= end:
                    return branch
            else:  # Handles wraparound like (23, 0)
                if hour >= start or hour <= end:
                    return branch
        return None

    def calculate_ming_gong_by_hour(gender, birth_hour):
        hour_branch = get_hour_branch(birth_hour)
        if not hour_branch:
            return {"error": "Invalid hour"}

        map_mg = {
            '子': '寅', '丑': '丑', '寅': '子', '卯': '亥',
            '辰': '戌', '巳': '酉', '午': '申', '未': '未',
            '申': '午', '酉': '巳', '戌': '辰', '亥': '卯',
        }

        return app.response_class(
            response=json.dumps({
                "hour_branch": hour_branch,
                "ming_gong": map_mg.get(hour_branch),
                "gender": gender
            }, ensure_ascii=False, indent=2),
            status=200,
            mimetype='application/json'
        )

    birth_hour = int(request.args.get("hour", 8))
    gender = request.args.get("gender", "阳男")
    return calculate_ming_gong_by_hour(gender, birth_hour)

# 🧠 Zodiac Sign logic (optional)
@app.route("/zodiac")
def zodiac_sign():
    birthdate_str = request.args.get("birthdate", None)

    if not birthdate_str:
        return jsonify({"zodiac": "Unknown"})

    try:
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
        month, day = birthdate.month, birthdate.day
    except ValueError:
        return jsonify({"zodiac": "Invalid date format"})

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

    def is_in_range(start, end, m, d):
        if start[0] < end[0] or (start[0] == end[0] and start[1] <= end[1]):
            return (m == start[0] and d >= start[1]) or \
                   (m == end[0] and d <= end[1]) or \
                   (start[0] < m < end[0])
        else:
            return (m == start[0] and d >= start[1]) or \
                   (m == end[0] and d <= end[1]) or \
                   (m > start[0] or m < end[0])

    for start, end, sign in zodiac_dates:
        if is_in_range(start, end, month, day):
            return jsonify({"zodiac": sign})

    return jsonify({"zodiac": "Unknown"})


    return app.response_class(
        response=json.dumps({"zodiac": "Unknown"}, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json'
    )

@app.route("/fortune", methods=["POST"])
def fortune():
    try:
        data = request.get_json()
        dob = data.get("dob")       # Format: "YYYY-MM-DD"
        time = data.get("time")     # Format: "HH:MM"
        gender = data.get("gender")

        birthdate = datetime.strptime(dob, "%Y-%m-%d")
        month, day = birthdate.month, birthdate.day

        birthday_key = f"{month:02d}-{day:02d}"
        profile = birthday_profiles.get(birthday_key, {})

        # Dummy fortune logic for now
        return jsonify({
            "zodiac": "Placeholder",
            "personality": profile.get("character", "Mysterious being..."),
            "lucky_day": "Every Thursday",
            "score": 88,
            "lucky_numbers": [3, 8, 21],
            "life_path": 5,
            "life_path_meaning": "Adventurous & expressive",
            "character": profile.get("character", ""),
            "character_advice": "Be bold, not reckless.",
            "love": profile.get("love", ""),
            "love_advice": "Love flows when you pause.",
            "wealth": profile.get("wealth", "Potential untapped."),
            "wealth_advice": "Seize the hidden doors.",
            "mindset": "Visionary but scattered",
            "mindset_tip": "Focus on fewer goals.",
            "emotion": "Deep but guarded",
            "emotion_advice": "Let others in.",
            "habits": "Spontaneous, sometimes inconsistent",
            "habits_insight": "Routine builds power.",
            "creativity": "Very high",
            "creativity_advice": "Don’t let doubt delay release.",
            "quote": profile.get("quote", "Stars whisper to those who listen.")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✨ Destiny Oracle endpoint
@app.route("/oracle", methods=["POST"])
def oracle():
    try:
        data = request.get_json()
        dob = data.get("dob")       # YYYY-MM-DD
        tob = data.get("tob")       # HH:MM
        tz = data.get("tz", "Asia/Singapore")

        # Prompt for GPT
        prompt = f"""
        You are a mystical Oracle. Write a short poetic destiny insight
        for someone born on {dob} at {tob} ({tz}).
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180
        )

        message = response.choices[0].message.content.strip()
        return jsonify({"result": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔥 FLASK RUNNER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    # allow only your site; if you're testing from other places temporarily use "*"
CORS(app, resources={r"/oracle": {"origins": ["https://aidoshop.com", "https://www.aidoshop.com"]}})



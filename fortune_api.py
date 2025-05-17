from flask import Flask, request, jsonify
import datetime
import random
import json

# Load birthday profiles from JSON
with open("january_birthdays.json", "r", encoding="utf-8") as f:
    birthday_profiles = json.load(f)
app = Flask(__name__)

ZODIAC_SIGNS = [
    ("Capricorn", (12, 22), (1, 19), "🧱 Steady, determined, and quietly lucky."),
    ("Aquarius", (1, 20), (2, 18), "🔮 Visionary thinker with unpredictable fortune."),
    ("Pisces", (2, 19), (3, 20), "🌊 Intuitive and dreamy, with hidden windfalls."),
    ("Aries", (3, 21), (4, 19), "🔥 Bold and impulsive, fortune favors your fire."),
    ("Taurus", (4, 20), (5, 20), "🌱 Practical and consistent, slow-building luck."),
    ("Gemini", (5, 21), (6, 20), "🌬 Witty and curious, luck dances with your ideas."),
    ("Cancer", (6, 21), (7, 22), "🌕 Emotional and nurturing, secret luck flows."),
    ("Leo", (7, 23), (8, 22), "🦁 Confident and radiant, star of fortune."),
    ("Virgo", (8, 23), (9, 22), "🌾 Analytical and humble, luck in the details."),
    ("Libra", (9, 23), (10, 22), "⚖️ Balanced and charming, graceful fortunes."),
    ("Scorpio", (10, 23), (11, 21), "🦂 Intense and strategic, luck in deep moves."),
    ("Sagittarius", (11, 22), (12, 21), "🏹 Adventurous and bold, lucky shots."),
]

def get_zodiac(month, day):
    for sign, start, end, description in ZODIAC_SIGNS:
        if (month == start[0] and day >= start[1]) or (month == end[0] and day <= end[1]):
            return sign, description
    return "Unknown", "Mystery surrounds your cosmic path."

def generate_lucky_day(birthdate):
    today = datetime.date.today()
    seed = int(birthdate.strftime("%Y%m%d"))
    random.seed(seed)
    days_ahead = random.randint(3, 30)
    return today + datetime.timedelta(days=days_ahead)

def generate_lucky_numbers(birthdate):
    seed = int(birthdate.strftime("%d%m%Y"))
    random.seed(seed)
    return sorted(random.sample(range(1, 50), 6))

@app.route('/fortune', methods=['POST'])
def get_fortune():
    data = request.json
    dob_str = data.get('dob')
    birth_time = data.get('time')
    gender = data.get('gender')

    try:
        birthdate = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    zodiac, personality = get_zodiac(birthdate.month, birthdate.day)
    lucky_day = generate_lucky_day(birthdate)
    score = random.randint(10, 20)
    lucky_numbers = generate_lucky_numbers(birthdate)

    # 👇 Use birthdate after it's created
    dob_key = birthdate.strftime("%m-%d")
    birthday_profile = birthday_profiles.get(dob_key, {
        "character": "Profile not available.",
        "love": "Love is a journey waiting to be explored.",
        "quote": "Write your own story, one star at a time."
    })

    result = {
        "zodiac": zodiac,
        "personality": personality,
        "lucky_day": lucky_day.strftime("%Y-%m-%d"),
        "score": score,
        "lucky_numbers": " • ".join(map(str, lucky_numbers)),
        "character": birthday_profile["character"],
        "love": birthday_profile["love"],
        "quote": birthday_profile["quote"]
    }

    return jsonify(result)
    data = request.json
    dob_str = data.get('dob')
    birth_time = data.get('time')
    gender = data.get('gender')

    try:
        birthdate = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    zodiac, personality = get_zodiac(birthdate.month, birthdate.day)
    lucky_day = generate_lucky_day(birthdate)
    lucky_numbers = generate_lucky_numbers(birthdate)

    return jsonify({
        "zodiac_sign": zodiac,
        "personality_summary": personality,
        "windfall_day": lucky_day.strftime("%Y-%m-%d"),
        "lucky_numbers": lucky_numbers
    })

if __name__ == '__main__':
    app.run(debug=True)

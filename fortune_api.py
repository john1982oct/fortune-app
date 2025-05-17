from flask import Flask, request, render_template_string
import datetime
import random
import json

# Load birthday profiles from JSON
with open("january_birthdays.json", "r", encoding="utf-8") as f:
    birthday_profiles = json.load(f)

app = Flask(__name__)

ZODIAC_SIGNS = [
    ("Capricorn", (12, 22), (1, 19), "🧱 Steady, determined, and quietly lucky."),
    ("Aquarius", (1, 20), (2, 18), "🧠 Visionary thinker with unpredictable fortune."),
    ("Pisces", (2, 19), (3, 20), "🌊 Intuitive and dreamy, with hidden windfalls."),
    ("Aries", (3, 21), (4, 19), "🔥 Bold and impulsive, fortune favors your fire."),
    ("Taurus", (4, 20), (5, 20), "🪵 Practical and consistent, slow-building luck."),
    ("Gemini", (5, 21), (6, 20), "🪶 Witty and curious, luck dances with your ideas."),
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

HTML_TEMPLATE = """
<h2>Your Results 🪄</h2>
<p><strong>Zodiac Sign:</strong> {{ result['zodiac'] }}</p>
<p><strong>Personality:</strong> {{ result['personality'] }}</p>
<p><strong>Lucky Windfall Day:</strong> {{ result['lucky_day'] }} (Score: {{ result['score'] }})</p>
<p><strong>Your Lucky Numbers:</strong> {{ result['lucky_numbers'] }}</p>
<hr>
<p><strong>Character Traits:</strong> {{ result['character'] }}</p>
<p><strong>Romantic Outlook:</strong> {{ result['love'] }}</p>
<p><strong>Quote of the Day:</strong> <em>“{{ result['quote'] }}”</em></p>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        dob_str = request.form.get("dob")
        try:
            birthdate = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
            zodiac, personality = get_zodiac(birthdate.month, birthdate.day)
            lucky_day = generate_lucky_day(birthdate).strftime("%Y-%m-%d")
            lucky_numbers = " • ".join(map(str, generate_lucky_numbers(birthdate)))
            score = random.randint(10, 20)

            dob_key = birthdate.strftime("%m-%d")
            birthday_profile = birthday_profiles.get(dob_key, {
                "character": "🌀 Profile not found.",
                "love": "💕 Love is still a mystery today.",
                "quote": "✨ Write your own destiny."
            })

            result = {
                "zodiac": zodiac,
                "personality": personality,
                "lucky_day": lucky_day,
                "score": score,
                "lucky_numbers": lucky_numbers,
                "character": birthday_profile["character"],
                "love": birthday_profile["love"],
                "quote": birthday_profile["quote"]
            }
        except Exception as e:
            result = {"error": f"Invalid input: {e}"}
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

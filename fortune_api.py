from flask import Flask, request, render_template_string
import datetime
import random
import json

app = Flask(__name__)

# Load birthday profiles from JSON
with open("january_birthdays.json", "r", encoding="utf-8") as f:
    birthday_profiles = json.load(f)

ZODIAC_SIGNS = [
    ("Capricorn", (12, 22), (1, 19), "🧱 Steady, determined, and quietly lucky."),
    ("Aquarius", (1, 20), (2, 18), "🧠 Visionary thinker with unpredictable fortune."),
    ("Pisces", (2, 19), (3, 20), "🌊 Intuitive and dreamy, with hidden windfalls."),
    ("Aries", (3, 21), (4, 19), "🔥 Bold and impulsive, fortune favors your fire."),
    ("Taurus", (4, 20), (5, 20), "🌿 Practical and consistent, slow-building luck."),
    ("Gemini", (5, 21), (6, 20), "🌀 Witty and curious, luck dances with your ideas."),
    ("Cancer", (6, 21), (7, 22), "🌊 Emotional and nurturing, secret luck flows."),
    ("Leo", (7, 23), (8, 22), "🌞 Confident and radiant, star of fortune."),
    ("Virgo", (8, 23), (9, 22), "🧩 Analytical and humble, luck in the details."),
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

HTML_TEMPLATE = '''
<html>
<head><title>Fortune Teller</title></head>
<body>
    <h2>🔮 Discover Your Lucky Day & Numbers</h2>
    <form method="POST" action="/fortune">
        Date of Birth (YYYY-MM-DD): <input type="text" name="dob"><br>
        Time of Birth (HH:MM): <input type="text" name="time"><br>
        Gender:
        <select name="gender">
            <option value="Male">Male</option>
            <option value="Female">Female</option>
        </select><br><br>
        <input type="submit" value="Reveal My Fortune 🧚‍♀️">
    </form>
    {% if result %}
    <hr>
    <h3>Your Results ✨</h3>
    <b>Zodiac Sign:</b> {{ result.zodiac }}<br>
    <b>Personality:</b> {{ result.personality }}<br>
    <b>Lucky Windfall Day:</b> {{ result.lucky_day }} (Score: {{ result.score }})<br>
    <b>Your Lucky Numbers:</b> {{ result.lucky_numbers }}<br><br>
    <b>Character Traits:</b> {{ result.character }}<br>
    <b>Romantic Outlook:</b> {{ result.love }}<br>
    <b>Quote of the Day:</b> “{{ result.quote }}”
    {% endif %}
</body>
</html>
'''

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, result=None)

@app.route("/fortune", methods=["POST"])
def get_fortune():
    try:
        dob_str = request.form.get("dob")
        birthdate = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
        dob_key = birthdate.strftime("%m-%d")
        birth_time = request.form.get("time")
        gender = request.form.get("gender")

        zodiac, personality = get_zodiac(birthdate.month, birthdate.day)
        lucky_day = generate_lucky_day(birthdate).strftime("%Y-%m-%d")
        score = random.randint(10, 20)
        lucky_numbers = " • ".join(map(str, generate_lucky_numbers(birthdate)))

        profile = birthday_profiles.get(dob_key, {
            "character": "Profile not available.",
            "love": "Love is a journey waiting to be explored.",
            "quote": "Write your own story, one star at a time."
        })

        result = {
            "zodiac": zodiac,
            "personality": personality,
            "lucky_day": lucky_day,
            "score": score,
            "lucky_numbers": lucky_numbers,
            "character": profile["character"],
            "love": profile["love"],
            "quote": profile["quote"]
        }
        return render_template_string(HTML_TEMPLATE, result=result)

    except Exception as e:
        return f"<h3>Error:</h3> {str(e)}", 400

if __name__ == "__main__":
    app.run(debug=True)

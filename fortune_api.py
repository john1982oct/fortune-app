from flask import Flask, request, jsonify, render_template
import json, os
from datetime import datetime
from openai import OpenAI
from flask_cors import CORS

# OpenAI client (reads OPENAI_API_KEY from env on Render)
client = OpenAI()

app = Flask(__name__)

# --- CORS: allow only your production origins (explicit, no wildcard)
ALLOWED_ORIGINS = {"https://aidoshop.com", "https://www.aidoshop.com"}
CORS(
    app,
    resources={
        r"/oracle": {"origins": list(ALLOWED_ORIGINS)},
        r"/fortune": {"origins": list(ALLOWED_ORIGINS)},
        r"/zodiac": {"origins": list(ALLOWED_ORIGINS)},
        r"/minggong": {"origins": list(ALLOWED_ORIGINS)},
    },
)

@app.after_request
def add_cors_headers(resp):
    """
    Extra safety: ensure preflight/response headers are present for our routes.
    This helps when a proxy/CDN strips headers or when Flask-CORS misses a path.
    """
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS and request.path in ("/oracle", "/fortune", "/zodiac", "/minggong"):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp

@app.route("/")
def home():
    return render_template("index.html")

# ---------- Data loaders ----------
# Birthday data
try:
    with open("birthdays_full.json", "r", encoding="utf-8") as f:
        birthday_profiles = json.load(f)
except Exception as e:
    birthday_profiles = {}
    print("⚠️ Failed to load birthdays:", e)

# Zi Wei pattern loader
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
            mimetype="application/json",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

# ---------- Helpers / utilities ----------
def _get_hour_branch(hour):
    hour = hour % 24
    ranges = [
        ((23, 0), "子"), ((1, 2), "丑"), ((3, 4), "寅"), ((5, 6), "卯"),
        ((7, 8), "辰"), ((9,10), "巳"), ((11,12), "午"), ((13,14), "未"),
        ((15,16), "申"), ((17,18), "酉"), ((19,20), "戌"), ((21,22), "亥"),
    ]
    for (start, end), br in ranges:
        if start < end:
            if start <= hour <= end:
                return br
        else:
            if hour >= start or hour <= end:
                return br
    return None

@app.route("/minggong", methods=["GET", "OPTIONS"])
def get_ming_gong():
    if request.method == "OPTIONS":
        return ("", 204)

    birth_hour = int(request.args.get("hour", 8))
    gender = request.args.get("gender", "阳男")

    hour_branch = _get_hour_branch(birth_hour)
    if not hour_branch:
        return jsonify({"error": "Invalid hour"}), 400

    map_mg = {
        "子": "寅", "丑": "丑", "寅": "子", "卯": "亥",
        "辰": "戌", "巳": "酉", "午": "申", "未": "未",
        "申": "午", "酉": "巳", "戌": "辰", "亥": "卯",
    }

    return app.response_class(
        response=json.dumps(
            {"hour_branch": hour_branch, "ming_gong": map_mg.get(hour_branch), "gender": gender},
            ensure_ascii=False, indent=2
        ),
        status=200,
        mimetype="application/json",
    )

@app.route("/zodiac", methods=["GET", "OPTIONS"])
def zodiac_sign():
    if request.method == "OPTIONS":
        return ("", 204)

    birthdate_str = request.args.get("birthdate", None)
    if not birthdate_str:
        return jsonify({"zodiac": "Unknown"})

    try:
        birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
        month, day = birthdate.month, birthdate.day
    except ValueError:
        return jsonify({"zodiac": "Invalid date format"})

    zodiac_dates = [
        ((1,20), (2,18), "Aquarius"),
        ((2,19), (3,20), "Pisces"),
        ((3,21), (4,19), "Aries"),
        ((4,20), (5,20), "Taurus"),
        ((5,21), (6,20), "Gemini"),
        ((6,21), (7,22), "Cancer"),
        ((7,23), (8,22), "Leo"),
        ((8,23), (9,22), "Virgo"),
        ((9,23), (10,22), "Libra"),
        ((10,23), (11,21), "Scorpio"),
        ((11,22), (12,21), "Sagittarius"),
        ((12,22), (1,19), "Capricorn"),
    ]

    def in_range(start, end, m, d):
        if start[0] < end[0] or (start[0] == end[0] and start[1] <= end[1]):
            return (m == start[0] and d >= start[1]) or (m == end[0] and d <= end[1]) or (start[0] < m < end[0])
        else:
            return (m == start[0] and d >= start[1]) or (m == end[0] and d <= end[1]) or (m > start[0] or m < end[0])

    for start, end, sign in zodiac_dates:
        if in_range(start, end, month, day):
            return jsonify({"zodiac": sign})
    return jsonify({"zodiac": "Unknown"})

@app.route("/fortune", methods=["POST", "OPTIONS"])
def fortune():
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        data = request.get_json(silent=True) or {}
        dob = data.get("dob")       # YYYY-MM-DD
        _time = data.get("time")    # HH:MM
        gender = data.get("gender")

        birthdate = datetime.strptime(dob, "%Y-%m-%d")
        month, day = birthdate.month, birthdate.day

        birthday_key = f"{month:02d}-{day:02d}"
        profile = birthday_profiles.get(birthday_key, {})

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
            "quote": profile.get("quote", "Stars whisper to those who listen."),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Destiny Oracle ----------
@app.route("/oracle", methods=["POST", "OPTIONS"])
def oracle():
    # Handle preflight quickly
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        data = request.get_json(silent=True) or {}
        # Accept both naming styles from frontend
        dob = data.get("dob")
        tob = data.get("tob") or data.get("time")
        tz = data.get("tz") or data.get("timezone") or "Asia/Singapore"

        # Minimal guardrails
        if not dob:
            return jsonify({"error": "Missing 'dob' (YYYY-MM-DD)"}), 400

        prompt = (
            f"You are a mystical Oracle. Write a short poetic destiny insight "
            f"for someone born on {dob}" + (f" at {tob}" if tob else "") + f" ({tz}). "
            "Keep it evocative, 6–10 lines, gentle and encouraging."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=180,
        )
        message = response.choices[0].message.content.strip()
        return jsonify({"text": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# (Optional) quick health/version endpoints
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/version")
def version():
    return {"version": os.environ.get("RELEASE_SHA", "local-dev")}

# Dev runner (Render uses gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

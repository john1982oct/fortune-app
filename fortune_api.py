from flask import Flask, request, jsonify, render_template
import json, os, random
from datetime import datetime, timedelta
from openai import OpenAI
from flask_cors import CORS

# OpenAI client
client = OpenAI()

app = Flask(__name__)

# --- CORS
ALLOWED_ORIGINS = {"https://aidoshop.com", "https://www.aidoshop.com"}
CORS(app, resources={r"/*": {"origins": list(ALLOWED_ORIGINS)}})

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp

@app.route("/")
def home():
    return render_template("index.html")

# ---------- Load data ----------
try:
    with open("birthdays_full.json", "r", encoding="utf-8") as f:
        birthday_profiles = json.load(f)
except Exception:
    birthday_profiles = {}

# ---------- Helpers ----------
def _parse_date_flex(s: str) -> datetime:
    """Accept YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY formats."""
    if not s:
        raise ValueError("Missing dob")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid dob format: {s}")

def _collect_payload():
    """Collect payload from JSON, form, or query params."""
    data = request.get_json(silent=True) or {}
    if not data:
        data = request.form.to_dict() or {}
    if not data:
        data = request.args.to_dict() or {}
    return data

# ---------- Zodiac ----------
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

# ---------- Life Path meanings ----------
life_path_meanings = {
    1: "Leader and pioneer. Independent, driven, full of fresh ideas.",
    2: "Peacemaker and partner. Balanced, diplomatic, emotionally intelligent.",
    3: "Creative communicator. Inspires through words, art, and joyful energy.",
    4: "Builder and stabilizer. Values structure, hard work, trustworthiness.",
    5: "Adventurer and freedom seeker. Thrives on change, travel, excitement.",
    6: "Nurturer and healer. Protects loved ones, creates harmony at home.",
    7: "Thinker and seeker. Introspective, intuitive, spiritually aware.",
    8: "Ambitious powerhouse. Destined for success, leadership, wealth.",
    9: "Humanitarian dreamer. Uplifts others with wisdom and compassion.",
    11: "Spiritual illuminator. Inspires masses with intuition.",
    22: "Master builder. Turns big dreams into lasting legacies.",
    33: "Compassionate teacher. Leads with unconditional love."
}

# ---------- Lucky Numbers ----------
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
        life_path, day, month,
        num1 % 100, num2 % 100,
        num3 % 100, num4 % 100,
    ]))

    final_nums = sorted([n for n in all_nums if 1 <= n <= 49])[:7]
    return {
        "lucky_numbers": final_nums,
        "life_path": life_path,
        "life_path_meaning": life_path_meanings.get(life_path, "A unique force with uncommon traits.")
    }

# ---------- Zi Wei Ming Gong ----------
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
    return jsonify({"hour_branch": hour_branch, "ming_gong": map_mg.get(hour_branch), "gender": gender})

# ---------- Fortune ----------
@app.route("/fortune", methods=["POST", "OPTIONS"])
def fortune():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        data = _collect_payload()
        dob_date = _parse_date_flex(data.get("dob"))

        date_key = dob_date.strftime("%m-%d")
        month, day = dob_date.month, dob_date.day
        zodiac_sign = get_zodiac_sign(month, day)

        personality_map = {
            "Aries": "Bold and full of energy.", "Taurus": "Grounded and loyal.",
            "Gemini": "Curious and quick-witted.", "Cancer": "Sensitive and nurturing.",
            "Leo": "Confident and charismatic.", "Virgo": "Practical and detail-oriented.",
            "Libra": "Balanced and social.", "Scorpio": "Passionate and intuitive.",
            "Sagittarius": "Adventurous and optimistic.", "Capricorn": "Disciplined and responsible.",
            "Aquarius": "Innovative and independent.", "Pisces": "Compassionate and artistic."
        }
        personality = personality_map.get(zodiac_sign, "Unique and undefined.")

        lucky_day = (dob_date.replace(year=datetime.now().year) + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
        lucky_score = random.randint(70, 99)
        lucky_result = calculate_lucky_numbers(dob_date)
        profile = birthday_profiles.get(date_key, {})

        return jsonify({
            "zodiac": zodiac_sign, "personality": personality,
            "lucky_day": lucky_day, "score": lucky_score,
            "lucky_numbers": lucky_result["lucky_numbers"],
            "life_path": lucky_result["life_path"],
            "life_path_meaning": lucky_result["life_path_meaning"],
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
    except Exception as e:
        app.logger.exception("Error in /fortune")
        return jsonify({"error": str(e)}), 400

# ---------- Ziwei Test (proxy for now) ----------
@app.route("/ziwei_test", methods=["GET", "POST", "OPTIONS"])
def ziwei_test():
    """Temporary: call fortune() so front-end still gets results without Zi Wei extraction."""
    if request.method == "OPTIONS":
        return ("", 204)
    return fortune()

# ---------- Oracle ----------
@app.route("/oracle", methods=["POST", "OPTIONS"])
def oracle():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        data = _collect_payload()
        dob = data.get("dob")
        tob = data.get("tob") or data.get("time")
        tz = data.get("tz") or data.get("timezone") or "Asia/Singapore"
        if not dob:
            return jsonify({"error": "Missing 'dob'"}), 400

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
        app.logger.exception("Error in /oracle")
        return jsonify({"error": str(e)}), 500

# ---------- Health ----------
@app.get("/health")
def health():
    return {"ok": True}

# ---------- Zodiac (NEW) ----------
@app.route("/zodiac", methods=["GET"])
def zodiac():
    birthdate = request.args.get("birthdate")
    if not birthdate:
        return jsonify({"error": "Missing 'birthdate' in YYYY-MM-DD format"}), 400
    try:
        dt = datetime.strptime(birthdate, "%Y-%m-%d")
        return jsonify({"zodiac": get_zodiac_sign(dt.month, dt.day)})
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

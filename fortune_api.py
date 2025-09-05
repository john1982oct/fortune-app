# fortune_api.py
from flask import Flask, request, jsonify, render_template
import json, os, random, hashlib
from datetime import datetime, timedelta
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
        r"/oracle":   {"origins": list(ALLOWED_ORIGINS)},
        r"/fortune":  {"origins": list(ALLOWED_ORIGINS)},
        r"/zodiac":   {"origins": list(ALLOWED_ORIGINS)},
        r"/minggong": {"origins": list(ALLOWED_ORIGINS)},
        r"/ziwei_test": {"origins": list(ALLOWED_ORIGINS)},
    },
)

@app.after_request
def add_cors_headers(resp):
    """
    Extra safety: ensure preflight/response headers are present for our routes.
    This helps when a proxy/CDN strips headers or when Flask-CORS misses a path.
    """
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS and request.path in ("/oracle", "/fortune", "/zodiac", "/minggong", "/ziwei_test"):
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
def _get_hour_branch(hour: int):
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

# Western zodiac (helper for both /zodiac and /fortune)
def _get_western_zodiac(month:int, day:int) -> str:
    zodiac_dates = [
        ((1,20),(2,18),"Aquarius"), ((2,19),(3,20),"Pisces"),
        ((3,21),(4,19),"Aries"),    ((4,20),(5,20),"Taurus"),
        ((5,21),(6,20),"Gemini"),   ((6,21),(7,22),"Cancer"),
        ((7,23),(8,22),"Leo"),      ((8,23),(9,22),"Virgo"),
        ((9,23),(10,22),"Libra"),   ((10,23),(11,21),"Scorpio"),
        ((11,22),(12,21),"Sagittarius"), ((12,22),(1,19),"Capricorn"),
    ]
    for (sm, sd), (em, ed), name in zodiac_dates:
        if (month == sm and day >= sd) or (month == em and day <= ed):
            return name
    return "Capricorn"

# Numerology helpers
def _reduce(n:int) -> int:
    """Reduce to 1–9; keep master 11/22/33."""
    while n > 9 and n not in (11,22,33):
        n = sum(int(d) for d in str(n))
    return n

def _life_path(dt: datetime) -> int:
    return _reduce(sum(int(d) for d in dt.strftime("%Y%m%d")))

_LIFE_PATH_MEANINGS = {
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
    33: "Compassionate teacher. You lead through unconditional love and service.",
}

def _lucky_7(dt: datetime) -> list[int]:
    """
    7 unique numbers in 1..49, deterministic from DOB, lightly biased
    toward life-path resonance & DOB digits.
    """
    lp = _life_path(dt)
    seed = int(hashlib.sha1(dt.strftime("%Y%m%d").encode("utf-8")).hexdigest(), 16)
    rng = random.Random(seed)

    base = list(range(1, 50))
    favored = {n for n in base if n % 9 == lp % 9}
    digits = [int(x) for x in dt.strftime("%Y%m%d")]
    favored |= {d for d in digits if 1 <= d <= 49}

    weighted = []
    for n in base:
        weighted.extend([n] * (3 if n in favored else 1))

    picks, seen = [], set()
    while len(picks) < 7 and weighted:
        n = rng.choice(weighted)
        if n not in seen:
            picks.append(n); seen.add(n)
        weighted = [w for w in weighted if w != n]
    return sorted(picks)

def _partner_date(dt_birth: datetime) -> str:
    """
    Choose a relationship-friendly date in next 60 days:
    match (month+day) reduced with life path OR weekday resonance.
    Deterministic using DOB as seed.
    """
    lp = _life_path(dt_birth)
    today = datetime.now().date()
    cands = []
    for i in range(1, 61):
        d = today + timedelta(days=i)
        if _reduce(d.month + d.day) == lp or _reduce(d.isoweekday()) == _reduce(lp):
            cands.append(d)
    if not cands:
        cands = [today + timedelta(days=lp)]
    seed = int(hashlib.sha1(dt_birth.strftime("%Y%m%d").encode("utf-8")).hexdigest(), 16)
    return str(cands[seed % len(cands)])

# ---------- Zi Wei: 命宫 ----------
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

# ---------- Western Zodiac endpoint ----------
@app.route("/zodiac", methods=["GET", "OPTIONS"])
def zodiac_sign():
    if request.method == "OPTIONS":
        return ("", 204)

    birthdate_str = request.args.get("birthdate", None)
    if not birthdate_str:
        return jsonify({"zodiac": "Unknown"})

    try:
        dt = datetime.strptime(birthdate_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"zodiac": "Invalid date format"})

    return jsonify({"zodiac": _get_western_zodiac(dt.month, dt.day)})

# ---------- Fortune (character + 7 lucky nums + partner date) ----------
@app.route("/fortune", methods=["POST", "OPTIONS"])
def fortune():
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        data = request.get_json(silent=True) or {}
        dob = data.get("dob")       # YYYY-MM-DD (required)
        _time = data.get("time")    # HH:MM (optional)
        gender = data.get("gender") # optional

        if not dob:
            return jsonify({"error": "Missing 'dob' (YYYY-MM-DD)"}), 400

        birthdate = datetime.strptime(dob, "%Y-%m-%d")
        month, day = birthdate.month, birthdate.day

        # Profile by MM-DD key
        birthday_key = f"{month:02d}-{day:02d}"
        profile = birthday_profiles.get(birthday_key, {})

        # Real zodiac + personality
        zodiac = _get_western_zodiac(month, day)
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
            "Pisces": "Compassionate and artistic.",
        }
        personality = personality_map.get(zodiac, profile.get("character", "A unique spirit with untapped potential."))

        # Numerology pack
        life_path = _life_path(birthdate)
        lucky_numbers = _lucky_7(birthdate)                    # 7 unique (1..49)
        lucky_score   = 70 + (sum(lucky_numbers) % 30)         # 70..99 stable-ish
        lucky_day     = _partner_date(birthdate)               # auspicious date
        partner_match = _partner_date(birthdate)               # relationship date
        life_path_meaning = _LIFE_PATH_MEANINGS.get(life_path, "A unique force with uncommon traits.")

        return jsonify({
            "zodiac": zodiac,
            "personality": personality,
            "lucky_day": lucky_day,
            "partner_match_date": partner_match,
            "score": lucky_score,
            "lucky_numbers": lucky_numbers,         # <-- 7 numbers
            "life_path": life_path,
            "life_path_meaning": life_path_meaning,

            # Enrichment from birthdays_full.json
            "character": profile.get("character", ""),
            "character_advice": profile.get("character_advice", ""),
            "love": profile.get("love", ""),
            "love_advice": profile.get("love_advice", ""),
            "quote": profile.get("quote", "The stars whisper to those who listen."),
            "wealth": profile.get("wealth", ""),
            "wealth_advice": profile.get("wealth_advice", ""),
            "mindset": profile.get("mindset", ""),
            "mindset_tip": profile.get("mindset_tip", ""),
            "emotion": profile.get("emotion", ""),
            "emotion_advice": profile.get("emotion_advice", ""),
            "habits": profile.get("habits", ""),
            "habits_insight": profile.get("habits_insight", ""),
            "creativity": profile.get("creativity", ""),
            "creativity_advice": profile.get("creativity_advice", ""),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Destiny Oracle (poem) ----------
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

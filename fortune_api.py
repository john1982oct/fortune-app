from flask import Flask, request, jsonify, render_template
import json, os, random
from datetime import datetime

app = Flask(__name__)

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
    hour = hour % 24  # make sure 23 or 0 won't break
    hour_ranges = [
        ((23, 0), '子'), ((1, 2), '丑'), ((3, 4), '寅'), ((5, 6), '卯'),
        ((7, 8), '辰'), ((9, 10), '巳'), ((11, 12), '午'), ((13, 14), '未'),
        ((15, 16), '申'), ((17, 18), '酉'), ((19, 20), '戌'), ((21, 22), '亥')
    ]
    for (start, end), branch in hour_ranges:
        if start <= hour <= end or (start == 23 and hour == 0):
            return branch
    return None

    def calculate_ming_gong_by_hour(gender, birth_hour):
        hour_branch = get_hour_branch(birth_hour)
        if not hour_branch:
            return {"error": "Invalid hour"}
        
        map_mg = {
            '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳', '辰': '巳', '巳': '巳',
            '午': '午', '未': '未', '申': '申', '酉': '酉', '戌': '戌', '亥': '子'
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

    # 🧠 Get request args
    birth_hour = int(request.args.get("hour", 8))
    gender = request.args.get("gender", "阳男")
    return calculate_ming_gong_by_hour(gender, birth_hour)

# 🧠 Zodiac Sign logic (optional)
@app.route("/zodiac")
def zodiac_sign():
    month = int(request.args.get("month", 1))
    day = int(request.args.get("day", 1))

    zodiac_list = [
        "Capricorn", "Aquarius", "Pisces", "Aries", "Taurus", "Gemini",
        "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius"
    ]
    cutoffs = [
        (1, 20), (2, 19), (3, 21), (4, 20), (5, 21), (6, 21),
        (7, 23), (8, 23), (9, 23), (10, 23), (11, 22), (12, 22)
    ]

    for i, (m, d) in enumerate(cutoffs):
        if (month < m) or (month == m and day < d):
            sign = zodiac_list[i - 1]
            break
    else:
        sign = zodiac_list[-1]

    return app.response_class(
        response=json.dumps({"zodiac": sign}, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json'
    )

# 🔥 FLASK RUNNER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime, timedelta
import random
# 🔮 MING GONG CALCULATOR - Step 1 Integration

earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

hour_branch_mapping = {
    (23, 0): '子', (1, 2): '丑', (3, 4): '寅', (5, 6): '卯', (7, 8): '辰',
    (9, 10): '巳', (11, 12): '午', (13, 14): '未', (15, 16): '申',
    (17, 18): '酉', (19, 20): '戌', (21, 22): '亥'
}

def get_hour_branch(hour: int):
    for (start, end), branch in hour_branch_mapping.items():
        if start <= hour <= end:
            return branch
    return None

ming_gong_by_hour = {
    '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳', '辰': '巳',
    '巳': '午', '午': '未', '未': '申', '申': '酉', '酉': '戌',
    '戌': '亥', '亥': '子'
}

def calculate_ming_gong_by_hour(gender: str, birth_hour: int):
    hour_branch = get_hour_branch(birth_hour)
    if not hour_branch:
        return {"error": "Invalid birth hour"}
    if gender.lower() in ['male', '阳男']:
        ming_gong = ming_gong_by_hour.get(hour_branch)
    else:
        ming_gong = "Mapping not defined for this gender yet"
    return {
        "hour_branch": hour_branch,
        "ming_gong": ming_gong,
        "gender": gender
    }

app = Flask(__name__)

# Load birthday profile data
with open("birthdays_full.json", "r", encoding="utf-8") as f:
    birthday_profiles = json.load(f)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')
@app.route("/minggong")
def get_ming_gong():
    birth_hour = int(request.args.get("hour", 8))
    gender = request.args.get("gender", "阳男")

    with open("data/ziwei_zai_wu/minggong_yin.json", "r", encoding="utf-8") as f:
        minggong_yin_data = json.load(f)

    result = minggong_yin_data.get(str(birth_hour), {"message": "未找到命宫资料"})

    return jsonify(result)


# 🧠 Helper: Zodiac Sign + Personality
def get_zodiac_sign_and_personality(month, day):
    zodiac_dates = [
        ((1, 20), (2, 18), "Aquarius", "Innovative and independent."),
        ((2, 19), (3, 20), "Pisces", "Compassionate and artistic."),
        ((3, 21), (4, 19), "Aries", "Bold and full of energy."),
        ((4, 20), (5, 20), "Taurus", "Grounded and loyal."),
        ((5, 21), (6, 20), "Gemini", "Curious and quick-witted."),
        ((6, 21), (7, 22), "Cancer", "Sensitive and nurturing."),
        ((7, 23), (8, 22), "Leo", "Confident and charismatic."),
        ((8, 23), (9, 22), "Virgo", "Practical and detail-oriented."),
        ((9, 23), (10, 22), "Libra", "Balanced and social."),
        ((10, 23), (11, 21), "Scorpio", "Passionate and intuitive."),
        ((11, 22), (12, 21), "Sagittarius", "Adventurous and optimistic."),
        ((12, 22), (1, 19), "Capricorn", "Disciplined and responsible.")
    ]
    for start, end, sign, personality in zodiac_dates:
        if (month == start[0] and day >= start[1]) or (month == end[0] and day <= end[1]):
            return sign, personality
    return "Capricorn", "Disciplined and responsible."

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

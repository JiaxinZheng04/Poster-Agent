import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import math
import re


# ===================================================
# Page config
# ===================================================
st.set_page_config(
    page_title="GF Poster Agent",
    page_icon="🎨",
    layout="wide"
)


# ===================================================
# Poster type library
# ===================================================
POSTER_TYPES = {
    "closure_notice": "假期休市通知 / Holiday Market Closure Notice",
    "festival_greeting": "节日祝福海报 / Festival Greeting Poster"
}


# ===================================================
# Holiday library
# Used for auto-detection and manual searchable selection
# ===================================================
HOLIDAY_LIBRARY = {
    "auto": {
        "display_name": "Auto detect from prompt / 自动识别",
        "aliases": [],
        "theme": "auto"
    },
    "new_year": {
        "display_name": "元旦 / New Year",
        "aliases": ["元旦", "新年", "new year", "happy new year", "元旦新禧"],
        "theme": "new_year"
    },
    "spring_festival": {
        "display_name": "春节 / Chinese New Year",
        "aliases": ["春节", "春節", "新春", "农历新年", "農曆新年", "chinese new year", "spring festival"],
        "theme": "spring_festival"
    },
    "qingming": {
        "display_name": "清明节 / Ching Ming Festival",
        "aliases": ["清明", "清明节", "清明節", "ching ming"],
        "theme": "qingming"
    },
    "easter": {
        "display_name": "复活节 / Easter",
        "aliases": ["复活节", "復活節", "easter"],
        "theme": "easter"
    },
    "labour_day": {
        "display_name": "劳动节 / Labour Day",
        "aliases": ["劳动节", "勞動節", "labour day", "labor day", "may day"],
        "theme": "labour_day"
    },
    "buddha_birthday": {
        "display_name": "佛诞 / Buddha's Birthday",
        "aliases": ["佛诞", "佛誕", "buddha"],
        "theme": "buddha_birthday"
    },
    "dragon_boat": {
        "display_name": "端午节 / Dragon Boat Festival",
        "aliases": ["端午", "端午节", "端午節", "dragon boat"],
        "theme": "dragon_boat"
    },
    "hk_sar_day": {
        "display_name": "香港特别行政区成立纪念日 / HKSAR Establishment Day",
        "aliases": ["香港特别行政区成立纪念日", "香港特別行政區成立紀念日", "香港回归", "香港回歸", "hksar"],
        "theme": "hk_sar_day"
    },
    "mid_autumn": {
        "display_name": "中秋节 / Mid-Autumn Festival",
        "aliases": ["中秋", "中秋节", "中秋節", "mid-autumn", "mid autumn", "moon festival"],
        "theme": "mid_autumn"
    },
    "national_day": {
        "display_name": "国庆日 / National Day",
        "aliases": ["国庆", "國慶", "国庆日", "國慶日", "national day"],
        "theme": "national_day"
    },
    "chung_yeung": {
        "display_name": "重阳节 / Chung Yeung Festival",
        "aliases": ["重阳", "重陽", "重阳节", "重陽節", "chung yeung"],
        "theme": "chung_yeung"
    },
    "thanksgiving": {
        "display_name": "感恩节 / Thanksgiving",
        "aliases": ["感恩", "感恩节", "感恩節", "thanksgiving"],
        "theme": "thanksgiving"
    },
    "christmas": {
        "display_name": "圣诞节 / Christmas",
        "aliases": ["圣诞", "聖誕", "圣诞节", "聖誕節", "christmas", "merry christmas"],
        "theme": "christmas"
    }
}


# ===================================================
# Asset library
# Controlled asset range
# Renderer only draws elements from this library
# ===================================================
ASSET_LIBRARY = {
    "new_year": {
        "colors": ["#C91616", "#FFFFFF", "#FFD68A"],
        "assets": ["firework", "light_beam", "circle_pattern"],
        "tone": "modern, festive, hopeful"
    },
    "spring_festival": {
        "colors": ["#B71919", "#FFD68A", "#FFF4E0"],
        "assets": ["lantern", "firework", "red_packet", "gold_coin", "gold_cloud"],
        "tone": "festive, warm, prosperous, corporate"
    },
    "qingming": {
        "colors": ["#EDEAE2", "#8A9A5B", "#333333"],
        "assets": ["mountain", "mist", "branch", "bird"],
        "tone": "calm, elegant, restrained"
    },
    "easter": {
        "colors": ["#F7F3E8", "#D8A15D", "#6B7280"],
        "assets": ["soft_circle", "light_gradient", "calendar_card"],
        "tone": "soft, clear, professional"
    },
    "labour_day": {
        "colors": ["#C91616", "#FFD68A", "#FFF4E0"],
        "assets": ["gold_curve", "firework", "brand_symbol"],
        "tone": "energetic, positive, corporate"
    },
    "buddha_birthday": {
        "colors": ["#F3EFE2", "#D8A15D", "#333333"],
        "assets": ["sun", "cloud", "lotus_like_shape"],
        "tone": "peaceful, elegant, formal"
    },
    "dragon_boat": {
        "colors": ["#0F766E", "#F2C16B", "#FFF8E7"],
        "assets": ["wave", "boat_shape", "gold_curve"],
        "tone": "traditional, energetic, festive"
    },
    "hk_sar_day": {
        "colors": ["#B71919", "#FFD68A", "#FFFFFF"],
        "assets": ["city_silhouette", "firework", "brand_symbol"],
        "tone": "formal, celebratory, civic"
    },
    "mid_autumn": {
        "colors": ["#D99A3D", "#FFF2C6", "#7A4A12"],
        "assets": ["moon", "rabbit", "cloud", "branch", "water_reflection"],
        "tone": "warm, elegant, poetic, client-facing"
    },
    "national_day": {
        "colors": ["#B71919", "#FFD68A", "#FFF4E0"],
        "assets": ["firework", "gold_curve", "city_silhouette"],
        "tone": "grand, festive, formal"
    },
    "chung_yeung": {
        "colors": ["#F4F0E8", "#D99A4E", "#222222"],
        "assets": ["mountain", "sun", "ink_texture", "bird", "grass"],
        "tone": "traditional, calm, elegant"
    },
    "thanksgiving": {
        "colors": ["#F5D06F", "#D99A3D", "#7A4A12"],
        "assets": ["warm_light", "thanksgiving_card", "gold_gradient"],
        "tone": "warm, grateful, client-facing"
    },
    "christmas": {
        "colors": ["#C91616", "#0C6B4E", "#FFD68A"],
        "assets": ["christmas_tree", "star", "snowflake", "gift"],
        "tone": "festive, joyful, warm"
    }
}


# ===================================================
# Visual style library
# Affects overall layout style
# ===================================================
VISUAL_STYLE_LIBRARY = {
    "auto": "Auto based on holiday / 根据节日自动匹配",
    "ink_elegant": "水墨雅致",
    "red_gold": "红金节庆",
    "warm_gold": "暖金高级",
    "modern_brand": "现代品牌红"
}


# ===================================================
# Font loading
# ===================================================
def load_font(size, bold=False):
    """
    Load CJK-compatible font if available.
    For Streamlit Cloud, add packages.txt with:
    fonts-noto-cjk
    """
    font_paths = []

    if bold:
        font_paths.extend([
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        ])

    font_paths.extend([
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ])

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    return ImageFont.load_default()


# ===================================================
# Helper functions
# ===================================================
def image_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def add_noise_texture(img, opacity=12):
    w, h = img.size
    noise = Image.new("L", (w, h))
    pixels = noise.load()

    for i in range(w):
        for j in range(h):
            pixels[i, j] = random.randint(225, 255)

    noise_rgb = noise.convert("RGB")
    return Image.blend(img, noise_rgb, opacity / 255)


def draw_centered_text(draw, text, y, font, fill, width):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (width - text_w) // 2
    draw.text((x, y), text, fill=fill, font=font)


def draw_wrapped_text(draw, text, x, y, font, fill, max_width, line_gap=10):
    lines = []
    current = ""

    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char

    if current:
        lines.append(current)

    for line in lines:
        draw.text((x, y), line, fill=fill, font=font)
        y += font.size + line_gap

    return y


def detect_holiday_from_prompt(prompt):
    prompt_lower = prompt.lower()
    matches = []

    for holiday_key, data in HOLIDAY_LIBRARY.items():
        if holiday_key == "auto":
            continue

        for alias in data["aliases"]:
            if alias.lower() in prompt_lower:
                matches.append(holiday_key)
                break

    if len(matches) >= 1:
        return matches[0]

    return "chung_yeung"


def resolve_holiday(user_prompt, holiday_choice):
    if holiday_choice == "auto":
        return detect_holiday_from_prompt(user_prompt)
    return holiday_choice


def resolve_visual_style(holiday_key, visual_style_choice):
    if visual_style_choice != "auto":
        return visual_style_choice

    if holiday_key in ["chung_yeung", "qingming", "buddha_birthday"]:
        return "ink_elegant"

    if holiday_key in ["spring_festival", "national_day", "hk_sar_day"]:
        return "red_gold"

    if holiday_key in ["mid_autumn", "thanksgiving"]:
        return "warm_gold"

    if holiday_key in ["christmas", "new_year", "labour_day"]:
        return "modern_brand"

    return "red_gold"


def get_theme_profile(holiday_key):
    return ASSET_LIBRARY.get(holiday_key, ASSET_LIBRARY["chung_yeung"])


# ===================================================
# Drawing assets
# ===================================================
def draw_company_brand(draw, x, y, color="#B8A06A", scale=1.0):
    logo_font = load_font(int(40 * scale), bold=True)
    sub_font = load_font(int(17 * scale), bold=False)

    # Simple placeholder GF symbol
    draw.rounded_rectangle(
        [x, y + int(8 * scale), x + int(70 * scale), y + int(48 * scale)],
        radius=int(14 * scale),
        outline=color,
        width=max(2, int(5 * scale))
    )

    draw.text((x + int(88 * scale), y), "廣發證券（香港）", fill=color, font=logo_font)
    draw.text(
        (x + int(90 * scale), y + int(50 * scale)),
        "GF SECURITIES (HONG KONG)",
        fill=color,
        font=sub_font
    )


def draw_firework(draw, cx, cy, r, color="#FFD68A", width=3):
    for i in range(18):
        angle = 2 * math.pi * i / 18
        x1 = cx + int(math.cos(angle) * r * 0.3)
        y1 = cy + int(math.sin(angle) * r * 0.3)
        x2 = cx + int(math.cos(angle) * r)
        y2 = cy + int(math.sin(angle) * r)
        draw.line([x1, y1, x2, y2], fill=color, width=width)


def draw_lantern(draw, x, y, scale=1.0):
    red = "#D7261E"
    gold = "#F4C46A"
    w = int(70 * scale)
    h = int(110 * scale)

    draw.line([x + w // 2, y - int(35 * scale), x + w // 2, y], fill=gold, width=3)
    draw.ellipse([x, y, x + w, y + h], fill=red, outline=gold, width=3)
    draw.line([x + 8, y + h // 2, x + w - 8, y + h // 2], fill="#B71919", width=2)
    draw.rectangle([x + 20, y + h - 5, x + w - 20, y + h + 10], fill=gold)
    draw.line([x + w // 2, y + h + 10, x + w // 2, y + h + 45], fill=gold, width=2)


def draw_moon_scene(draw, width, height):
    draw.ellipse([190, 360, 710, 880], fill="#FFF4C8")
    draw.ellipse([235, 405, 665, 835], fill="#FBE7A5")

    # cloud
    draw.ellipse([430, 650, 620, 720], fill="#FFF9D8")
    draw.ellipse([540, 625, 720, 705], fill="#FFF9D8")
    draw.rectangle([430, 670, 720, 720], fill="#FFF9D8")

    # branch
    for i in range(5):
        draw.line([60, 410 + i * 30, 300, 320 + i * 20], fill="#8A5A20", width=4)

    # rabbit
    draw.ellipse([385, 735, 535, 880], fill="#DFAE45")
    draw.ellipse([430, 690, 470, 770], fill="#DFAE45")
    draw.ellipse([475, 690, 515, 770], fill="#DFAE45")

    # reflection
    for i in range(7):
        y = 905 + i * 22
        draw.arc([260 - i * 18, y, 640 + i * 18, y + 60], 10, 170, fill="#F7D879", width=3)


def draw_mountain_scene(draw, width, height):
    draw.ellipse([610, 220, 790, 400], fill="#E7A15F")

    draw.polygon([(0, 430), (130, 330), (250, 440)], fill="#D8D8D8")
    draw.polygon([(620, 520), (760, 410), (930, 520)], fill="#D0D0D0")
    draw.polygon([(360, 500), (520, 410), (690, 510)], fill="#E1E1E1")

    for bx, by in [(160, 280), (690, 430), (720, 450), (760, 440)]:
        draw.text((bx, by), "⌁", fill="#888888", font=load_font(26))

    for i in range(6):
        x = 40 + i * 20
        draw.arc([x, 520 - i * 8, x + 180, 760], 210, 285, fill="#C8B27D", width=2)


def draw_christmas_tree(draw, cx, cy):
    green = "#0C6B4E"
    gold = "#FFD68A"

    draw_firework(draw, cx, cy - 30, 35, gold)

    draw.polygon([(cx, cy), (cx - 170, cy + 260), (cx + 170, cy + 260)], fill=green)
    draw.polygon([(cx, cy + 160), (cx - 215, cy + 460), (cx + 215, cy + 460)], fill=green)
    draw.rectangle([cx - 36, cy + 460, cx + 36, cy + 575], fill=green)

    for px, py in [(cx - 100, cy + 210), (cx + 90, cy + 300), (cx - 60, cy + 400)]:
        draw.ellipse([px, py, px + 20, py + 20], fill=gold)


def draw_red_packet_scene(draw, width, height):
    # red packet / ticket inspired by previous posters
    draw.rounded_rectangle([250, 520, 650, 870], radius=32, fill="#FCE6B0")
    draw.rounded_rectangle([300, 570, 600, 830], radius=22, fill="#D92020")
    draw.ellipse([390, 640, 520, 770], fill="#F7B15A")

    # coins
    for x, y in [(160, 610), (700, 540), (720, 730), (220, 840)]:
        draw.ellipse([x, y, x + 46, y + 46], fill="#F6C453")
        draw.rectangle([x + 18, y + 14, x + 28, y + 32], fill="#D99A3D")


def draw_modern_geometry(draw, width, height, color="#E85A3C"):
    draw.polygon([(0, 300), (width, 160), (width, 520), (0, 620)], fill=color)
    draw.polygon([(210, 360), (560, 260), (350, 1220), (0, 1220)], fill="#A80F0F")
    draw.ellipse([520, 660, 950, 1090], fill="#E46B3E")
    draw.ellipse([610, 750, 850, 990], fill="#C91616")


def draw_wave_scene(draw, width, height):
    # dragon boat-ish wave
    for i in range(7):
        y = 670 + i * 28
        draw.arc([80 - i * 20, y, width - 80 + i * 20, y + 90], 180, 360, fill="#F2C16B", width=4)
    draw.polygon([(260, 550), (620, 550), (540, 640), (330, 640)], fill="#0F766E")
    draw.line([300, 535, 580, 535], fill="#F2C16B", width=6)


def draw_soft_light_scene(draw, width, height):
    for radius, alpha_color in [(560, "#F7E7A8"), (430, "#F5D06F"), (300, "#D99A3D")]:
        x1 = width // 2 - radius // 2
        y1 = 430 - radius // 2
        x2 = width // 2 + radius // 2
        y2 = 430 + radius // 2
        draw.ellipse([x1, y1, x2, y2], fill=alpha_color)


def draw_qr_placeholder(draw, width, height):
    draw.rounded_rectangle(
        [700, height - 170, 820, height - 50],
        radius=12,
        outline="#D8D8D8",
        width=3
    )
    draw.text((705, height - 25), "QR reserved", fill="#999999", font=load_font(18))


# ===================================================
# Content generation: rule-based poster_state
# ===================================================
def generate_poster_state(user_prompt, poster_type, holiday_choice, visual_style_choice):
    holiday_key = resolve_holiday(user_prompt, holiday_choice)
    visual_style = resolve_visual_style(holiday_key, visual_style_choice)
    theme = get_theme_profile(holiday_key)

    base = {
        "poster_type": poster_type,
        "holiday_key": holiday_key,
        "holiday_name": HOLIDAY_LIBRARY[holiday_key]["display_name"],
        "visual_style": visual_style,
        "colors": theme["colors"],
        "selected_assets": theme["assets"],
        "tone": theme["tone"]
    }

    if poster_type == "closure_notice":
        return generate_closure_state(base, holiday_key)

    return generate_greeting_state(base, holiday_key)


def generate_closure_state(base, holiday_key):
    # These are editable sample defaults.
    # For production use, replace with verified exchange schedules.
    default = {
        "holiday": "假期",
        "title": "休市通知",
        "subtitle": "請留意假期交易安排",
        "festival_label": "Holiday Notice",
        "year": "2026",
        "month": "1月",
        "calendar_dates": ["01", "02", "03", "04", "05", "06", "07"],
        "weekdays": ["周四", "周五", "周六", "周日", "周一", "周二", "周三"],
        "markets": [
            {"name": "港股", "closed_indices": [0, 2, 3]},
            {"name": "美股", "closed_indices": [0, 2, 3]},
            {"name": "港股通", "closed_indices": [0, 2, 3]},
            {"name": "滬、深股通", "closed_indices": [0, 2, 3]},
        ],
        "details_title": "假期休市安排：",
        "details": [
            "港股：請留意假期休市安排",
            "美股：請留意假期交易安排",
            "港股通及滬、深股通：請以官方公告為準",
            "*實際安排請以交易所公告為準。"
        ]
    }

    presets = {
        "new_year": {
            "holiday": "元旦",
            "title": "元旦新禧",
            "subtitle": "年首初月，歲如喜光",
            "festival_label": "New Year",
            "year": "2026",
            "month": "1月",
            "calendar_dates": ["29", "30", "31", "01", "02", "03", "04"],
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "markets": [
                {"name": "港股", "closed_indices": [3, 5, 6]},
                {"name": "美股", "closed_indices": [3, 5, 6]},
                {"name": "港股通", "closed_indices": [3, 5, 6]},
                {"name": "滬、深股通", "closed_indices": [3, 5, 6]},
            ],
            "details_title": "2026年元旦休市安排：",
            "details": [
                "港股：1月1日（周四）休市",
                "美股：1月1日（周四）休市",
                "港股通及滬、深股通：1月1日關閉",
                "*實際安排請以交易所公告為準。"
            ]
        },
        "spring_festival": {
            "holiday": "春節",
            "title": "新春快樂",
            "subtitle": "瑞氣迎新歲，萬事啟新程",
            "festival_label": "農曆新年",
            "year": "2026",
            "month": "2月",
            "calendar_dates": ["16", "17", "18", "19", "20", "21", "22"],
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "markets": [
                {"name": "港股", "closed_indices": [0, 1, 2, 5, 6]},
                {"name": "美股", "closed_indices": [0, 5, 6]},
                {"name": "港股通", "closed_indices": [0, 1, 2, 3, 4, 5, 6]},
                {"name": "滬、深股通", "closed_indices": [0, 1, 2, 3, 4, 5, 6]},
            ],
            "details_title": "2026年春節休市安排：",
            "details": [
                "港股：2月16日半日交易，下午休市",
                "港股：2月17日至19日全日休市",
                "港股通及滬、深股通安排請以官方公告為準",
                "*實際安排請以交易所公告為準。"
            ]
        },
        "mid_autumn": {
            "holiday": "中秋節",
            "title": "中秋節",
            "subtitle": "月滿人團圓，佳節共安康",
            "festival_label": "農曆八月十五",
            "year": "2026",
            "month": "9月",
            "calendar_dates": ["21", "22", "23", "24", "25", "26", "27"],
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "markets": [
                {"name": "港股", "closed_indices": [5, 6]},
                {"name": "美股", "closed_indices": [5, 6]},
                {"name": "港股通", "closed_indices": [5, 6]},
                {"name": "滬、深股通", "closed_indices": [5, 6]},
            ],
            "details_title": "2026年中秋節休市安排：",
            "details": [
                "中秋節前後交易安排請以交易所公告為準",
                "港股、美股及互聯互通安排請留意官方通知",
                "*實際安排請以交易所公告為準。"
            ]
        },
        "chung_yeung": {
            "holiday": "重陽節",
            "title": "重陽節",
            "subtitle": "登高攬秋光，歲歲皆綿長",
            "festival_label": "農曆九月初九",
            "year": "2025",
            "month": "10月",
            "calendar_dates": ["27", "28", "29", "30", "31", "01", "02"],
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "markets": [
                {"name": "港股", "closed_indices": [2, 5, 6]},
                {"name": "美股", "closed_indices": [5, 6]},
                {"name": "港股通", "closed_indices": [2, 5, 6]},
                {"name": "滬、深股通", "closed_indices": [2, 5, 6]},
            ],
            "details_title": "2025年重陽節休市安排：",
            "details": [
                "港股：10月29日（周三）休市",
                "美股：不受影響，正常開市",
                "港股通（南向）：10月29日關閉",
                "滬、深股通（北向）：10月29日關閉",
                "*11月1日、2日為周末休市。"
            ]
        },
        "thanksgiving": {
            "holiday": "感恩節",
            "title": "Thanksgiving",
            "subtitle": "感恩相伴，溫暖同行",
            "festival_label": "Thanksgiving Day",
            "year": "2025",
            "month": "11月",
            "calendar_dates": ["24", "25", "26", "27", "28", "29", "30"],
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "markets": [
                {"name": "港股", "closed_indices": [5, 6]},
                {"name": "美股", "closed_indices": [3, 5, 6]},
                {"name": "港股通", "closed_indices": [5, 6]},
                {"name": "滬、深股通", "closed_indices": [5, 6]},
            ],
            "details_title": "2025年感恩節休市安排：",
            "details": [
                "美股：11月27日（周四）休市一日",
                "美股：11月28日（周五）提前3小時收市",
                "港股及港股通不受影響，正常開市",
                "*實際安排請以交易所公告為準。"
            ]
        },
        "christmas": {
            "holiday": "聖誕節",
            "title": "MERRY CHRISTMAS",
            "subtitle": "聖誕快樂，喜樂常伴",
            "festival_label": "Christmas",
            "year": "2025",
            "month": "12月",
            "calendar_dates": ["22", "23", "24", "25", "26", "27", "28"],
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "markets": [
                {"name": "港股", "closed_indices": [3, 4, 5, 6]},
                {"name": "美股", "closed_indices": [3, 5, 6]},
                {"name": "港股通", "closed_indices": [3, 4, 5, 6]},
                {"name": "滬、深股通", "closed_indices": [3, 4, 5, 6]},
            ],
            "details_title": "2025年聖誕節休市安排：",
            "details": [
                "港股：12月25日至26日休市",
                "美股：12月25日休市",
                "港股通及滬、深股通安排請以官方公告為準",
                "*實際安排請以交易所公告為準。"
            ]
        }
    }

    closure = presets.get(holiday_key, default)
    closure.update(base)
    closure["poster_type"] = "closure_notice"

    return closure


def generate_greeting_state(base, holiday_key):
    presets = {
        "new_year": {
            "title": "元旦新禧",
            "subtitle": "HAPPY NEW YEAR",
            "blessing": "年首初月，歲如熹光。",
        },
        "spring_festival": {
            "title": "恭賀新春",
            "subtitle": "廣發證券（香港）祝您新春快樂",
            "blessing": "馬到功成，財源廣進。",
        },
        "mid_autumn": {
            "title": "情滿中秋\n月圓人團圓",
            "subtitle": "廣發證券（香港）祝您中秋快樂",
            "blessing": "月滿人團圓，佳節共安康。",
        },
        "christmas": {
            "title": "MERRY\nCHRISTMAS",
            "subtitle": "聖誕快樂",
            "blessing": "願節日的溫暖與喜悅常伴您左右。",
        },
        "thanksgiving": {
            "title": "Thanksgiving",
            "subtitle": "感恩相伴",
            "blessing": "感謝一路同行，願溫暖與收穫常伴左右。",
        },
        "chung_yeung": {
            "title": "重陽安康",
            "subtitle": "登高望遠，秋意綿長",
            "blessing": "廣發證券（香港）祝您重陽安康，順遂如意。",
        },
        "dragon_boat": {
            "title": "端午安康",
            "subtitle": "粽香盈袖，福至安康",
            "blessing": "廣發證券（香港）祝您端午安康。",
        },
        "national_day": {
            "title": "國慶快樂",
            "subtitle": "山河錦繡，盛世同慶",
            "blessing": "廣發證券（香港）祝您假期愉快。",
        },
        "hk_sar_day": {
            "title": "同慶華誕",
            "subtitle": "香港特別行政區成立紀念日",
            "blessing": "同心同行，共啟新程。",
        }
    }

    default = {
        "title": "節日快樂",
        "subtitle": "廣發證券（香港）祝您節日愉快",
        "blessing": "願您與家人平安喜樂，萬事順遂。",
    }

    greeting = presets.get(holiday_key, default)
    greeting.update(base)
    greeting["poster_type"] = "festival_greeting"

    return greeting


# ===================================================
# Render closure notice
# ===================================================
def render_closure_notice(state):
    width, height = 900, 1600
    colors = state["colors"]
    bg = colors[0]
    accent = colors[1]
    light = colors[2]
    visual_style = state["visual_style"]
    assets = state["selected_assets"]

    if visual_style == "ink_elegant":
        bg = "#F4F0E8"
        card = "#FFFFFF"
        title_color = "#111111"
        subtitle_color = "#333333"
    elif visual_style in ["red_gold", "modern_brand"]:
        bg = "#B71919"
        card = "#FFF8F0"
        title_color = "#FFF0C2"
        subtitle_color = "#FFF8E8"
    else:
        card = "#FFFFFF"
        title_color = "#111111"
        subtitle_color = "#333333"

    img = Image.new("RGB", (width, height), bg)
    img = add_noise_texture(img, opacity=14)
    draw = ImageDraw.Draw(img)

    title_font = load_font(86, bold=True)
    subtitle_font = load_font(30)
    small_font = load_font(25)
    medium_font = load_font(34)
    body_font = load_font(37)
    detail_font = load_font(33)

    # Top visual
    if visual_style == "ink_elegant":
        if "mountain" in assets or "ink_texture" in assets:
            draw_mountain_scene(draw, width, height)
        else:
            draw_soft_light_scene(draw, width, height)
    else:
        draw.rectangle([0, 0, width, 600], fill=bg)

        if "lantern" in assets:
            draw_lantern(draw, 40, 60, 0.9)
            draw_lantern(draw, width - 110, 60, 0.9)

        if "firework" in assets:
            draw_firework(draw, 220, 250, 60, "#FFD68A")
            draw_firework(draw, 720, 280, 70, "#FFD68A")

        if "red_packet" in assets:
            draw_red_packet_scene(draw, width, height)

        if "wave" in assets:
            draw_wave_scene(draw, width, height)

    # Header
    draw_centered_text(draw, state["title"], 120, title_font, title_color, width)
    draw_centered_text(draw, state["subtitle"], 250, subtitle_font, subtitle_color, width)

    # Festival label
    label_w, label_h = 240, 46
    label_x = (width - label_w) // 2
    draw.rounded_rectangle(
        [label_x, 330, label_x + label_w, 330 + label_h],
        radius=22,
        outline="#B8A06A",
        width=2,
        fill="#F7EFE3" if visual_style == "ink_elegant" else "#FFF3D3"
    )
    draw_centered_text(draw, state["festival_label"], 338, small_font, "#9A7A3D", width)

    # Calendar card
    card_x1, card_y1 = 45, 590
    card_x2, card_y2 = width - 45, 1470

    draw.rounded_rectangle(
        [card_x1, card_y1, card_x2, card_y2],
        radius=34,
        fill=card,
        outline="#E7E2D8",
        width=2
    )

    # Hanging pins
    pin_color = "#C8A36A"
    draw.rounded_rectangle([135, 560, 155, 640], radius=10, fill=pin_color)
    draw.rounded_rectangle([width - 155, 560, width - 135, 640], radius=10, fill=pin_color)

    # Year
    draw_centered_text(
        draw,
        f"- {state['year']} -",
        card_y1 + 55,
        load_font(52, bold=True),
        "#222222",
        width
    )

    # Month
    draw.text((85, card_y1 + 145), state["month"].replace("月", ""), fill="#333333", font=load_font(42, bold=True))
    draw.line([120, card_y1 + 165, 90, card_y1 + 205], fill="#333333", width=2)
    draw.text((118, card_y1 + 198), "月", fill="#333333", font=medium_font)

    # Date header
    start_x = 250
    col_w = 78
    header_y = card_y1 + 145

    for i, (weekday, date) in enumerate(zip(state["weekdays"], state["calendar_dates"])):
        x = start_x + i * col_w
        draw.text((x, header_y), weekday, fill="#777777", font=small_font)
        draw.text((x + 10, header_y + 48), date, fill="#222222", font=medium_font)

    # Market rows
    row_y = card_y1 + 265
    row_gap = 86

    for row in state["markets"]:
        draw.text((85, row_y + 10), row["name"], fill="#222222", font=body_font)

        for idx in row["closed_indices"]:
            if 0 <= idx < 7:
                cx = start_x + idx * col_w + 28
                cy = row_y + 24
                draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=accent)
                draw.text((cx - 17, cy - 19), "休", fill="#FFFFFF", font=medium_font)

        draw.line([85, row_y + 72, width - 85, row_y + 72], fill="#DADADA", width=1)
        row_y += row_gap

    # Details
    detail_y = card_y1 + 630
    draw.text((85, detail_y), state["details_title"], fill="#222222", font=load_font(42, bold=True))
    detail_y += 80

    for line in state["details"]:
        detail_y = draw_wrapped_text(
            draw,
            line,
            85,
            detail_y,
            detail_font,
            "#333333" if not line.startswith("*") else "#999999",
            max_width=720,
            line_gap=10
        )
        detail_y += 22

    # Company brand
    draw_company_brand(draw, 165, height - 115, color="#B8A06A", scale=0.78)

    return img


# ===================================================
# Render festival greeting
# ===================================================
def render_festival_greeting(state):
    width, height = 900, 1600
    colors = state["colors"]
    bg = colors[0]
    accent = colors[1]
    text_color = colors[2]
    visual_style = state["visual_style"]
    assets = state["selected_assets"]
    holiday_key = state["holiday_key"]

    if visual_style == "red_gold":
        bg = "#B71919"
        text_color = "#FFF4D6"
    elif visual_style == "modern_brand":
        bg = "#C91616"
        text_color = "#FFF4E0"
    elif visual_style == "warm_gold":
        bg = "#D99A3D"
        text_color = "#7A4A12"
    elif visual_style == "ink_elegant":
        bg = "#F4F0E8"
        text_color = "#222222"

    img = Image.new("RGB", (width, height), bg)
    img = add_noise_texture(img, opacity=8)
    draw = ImageDraw.Draw(img)

    title_font = load_font(78, bold=True)
    big_font = load_font(96, bold=True)
    subtitle_font = load_font(36)
    body_font = load_font(34)

    # Background motifs
    if visual_style == "warm_gold" or "moon" in assets:
        draw_moon_scene(draw, width, height)

    elif visual_style == "modern_brand":
        draw_modern_geometry(draw, width, height)
        if "firework" in assets:
            draw_firework(draw, 210, 1050, 90, "#FFF1C4")
            draw_firework(draw, 710, 680, 70, "#FFF1C4")

    elif visual_style == "ink_elegant":
        draw_mountain_scene(draw, width, height)

    else:
        if "lantern" in assets:
            draw_lantern(draw, 35, 80, 1.0)
            draw_lantern(draw, width - 105, 80, 1.0)

        if "firework" in assets:
            draw_firework(draw, 220, 360, 80, "#FFD68A")
            draw_firework(draw, 710, 430, 90, "#FFD68A")

        if "red_packet" in assets:
            draw_red_packet_scene(draw, width, height)

    # Company brand
    brand_color = "#E4D0A1" if bg.lower() not in ["#f4f0e8"] else "#B8A06A"
    draw_company_brand(draw, 70, 70, color=brand_color, scale=0.7)

    # Main title
    title_lines = state["title"].split("\n")
    title_y = 260

    for line in title_lines:
        font = big_font if len(line) <= 6 else title_font
        draw_centered_text(draw, line, title_y, font, text_color, width)
        title_y += font.size + 18

    draw_centered_text(draw, state["subtitle"], title_y + 40, subtitle_font, text_color, width)
    draw_centered_text(draw, state["blessing"], title_y + 105, body_font, text_color, width)

    # Holiday-specific main asset
    if "christmas_tree" in assets:
        draw_christmas_tree(draw, width // 2, 620)

    if "red_packet" in assets and holiday_key == "spring_festival":
        draw.text((270, 1010), "恭 賀 新 春", fill=text_color, font=load_font(60, bold=True))

    if "light_beam" in assets:
        draw.line([450, 340, 450, 760], fill="#FFF6DA", width=12)
        draw.ellipse([405, 240, 495, 330], fill="#FFF6DA")

    if "wave" in assets:
        draw_wave_scene(draw, width, height)

    # Bottom white wave area
    draw.pieslice([-160, height - 350, width + 160, height + 220], 180, 360, fill="#FFFFFF")
    draw_company_brand(draw, 70, height - 150, color="#B8A06A", scale=0.75)

    # QR reserved area
    draw_qr_placeholder(draw, width, height)

    return img


# ===================================================
# Main renderer
# ===================================================
def generate_poster(state):
    if state["poster_type"] == "closure_notice":
        return render_closure_notice(state)

    return render_festival_greeting(state)


# ===================================================
# Revision logic
# ===================================================
def revise_state(state, revision):
    updated = state.copy()
    r = revision.lower()

    if "正式" in revision or "formal" in r:
        if updated["poster_type"] == "festival_greeting":
            updated["subtitle"] = "廣發證券（香港）謹祝您節日愉快"
            updated["blessing"] = "願您與家人平安順遂，萬事如意。"

    if "简短" in revision or "簡短" in revision or "shorter" in r:
        if updated["poster_type"] == "festival_greeting":
            updated["blessing"] = "佳節愉快，萬事順遂。"
        else:
            updated["details"] = updated["details"][:3]

    if "温暖" in revision or "溫暖" in revision or "warm" in r:
        if updated["poster_type"] == "festival_greeting":
            updated["blessing"] = "願這份節日暖意，伴您與家人共度美好時光。"

    if "红色" in revision or "紅色" in revision or "red" in r:
        updated["visual_style"] = "red_gold"

    if "金色" in revision or "gold" in r:
        updated["visual_style"] = "warm_gold"

    if "水墨" in revision or "ink" in r:
        updated["visual_style"] = "ink_elegant"

    if "现代" in revision or "現代" in revision or "modern" in r:
        updated["visual_style"] = "modern_brand"

    return updated


# ===================================================
# Streamlit UI
# ===================================================
st.title("🎨 GF Securities Poster Agent")
st.write("Generate holiday market closure notices and festival greeting posters using controlled company-style assets.")

with st.sidebar:
    st.header("Poster Settings")

    poster_type = st.selectbox(
        "海报类型 / Poster Type",
        options=list(POSTER_TYPES.keys()),
        format_func=lambda x: POSTER_TYPES[x]
    )

    holiday_choice = st.selectbox(
        "节日主题 / Holiday Theme",
        options=list(HOLIDAY_LIBRARY.keys()),
        format_func=lambda x: HOLIDAY_LIBRARY[x]["display_name"]
    )

    visual_style_choice = st.selectbox(
        "视觉风格 / Visual Style",
        options=list(VISUAL_STYLE_LIBRARY.keys()),
        format_func=lambda x: VISUAL_STYLE_LIBRARY[x]
    )

    st.caption("Holiday Library")
    if holiday_choice != "auto":
        st.json(HOLIDAY_LIBRARY[holiday_choice])
    else:
        st.info("Holiday will be detected from your prompt.")

st.divider()

# ===================================================
# Generate poster
# ===================================================
st.subheader("1. Generate Poster")

default_prompt = (
    "生成一张2025年重阳节休市通知海报"
    if poster_type == "closure_notice"
    else "生成一张中秋节祝福海报，面向客户，语气正式温暖"
)

user_prompt = st.text_area(
    "输入海报指令 / Poster instruction",
    value=default_prompt,
    height=120
)

if st.button("Generate Poster"):
    if not user_prompt.strip():
        st.warning("Please enter a poster instruction.")
    else:
        state = generate_poster_state(
            user_prompt=user_prompt,
            poster_type=poster_type,
            holiday_choice=holiday_choice,
            visual_style_choice=visual_style_choice
        )

        st.session_state["poster_state"] = state

        poster = generate_poster(state)
        st.session_state["poster"] = poster

        st.success("Poster generated.")

        col1, col2 = st.columns([1.25, 1])

        with col1:
            st.image(poster, caption="Generated Poster Preview", use_container_width=False)

            st.download_button(
                label="Download Poster as PNG",
                data=image_to_bytes(poster),
                file_name="gf_generated_poster.png",
                mime="image/png"
            )

        with col2:
            st.subheader("Poster State")
            st.json(state)

st.divider()

# ===================================================
# Revise poster
# ===================================================
st.subheader("2. Revise Poster")

revision_prompt = st.text_area(
    "输入修改指令 / Revision instruction",
    placeholder="例如：语气更正式一点 / 改成红金风格 / 文案更简短 / 更温暖一点 / 改成水墨风格",
    height=100
)

if st.button("Apply Revision"):
    if "poster_state" not in st.session_state:
        st.warning("Please generate a poster first.")
    elif not revision_prompt.strip():
        st.warning("Please enter a revision instruction.")
    else:
        updated_state = revise_state(st.session_state["poster_state"], revision_prompt)

        st.session_state["poster_state"] = updated_state
        poster = generate_poster(updated_state)
        st.session_state["poster"] = poster

        st.success("Revision applied.")

        col1, col2 = st.columns([1.25, 1])

        with col1:
            st.image(poster, caption="Revised Poster Preview", use_container_width=False)

            st.download_button(
                label="Download Revised Poster as PNG",
                data=image_to_bytes(poster),
                file_name="gf_revised_poster.png",
                mime="image/png"
            )

        with col2:
            st.subheader("Updated Poster State")
            st.json(updated_state)

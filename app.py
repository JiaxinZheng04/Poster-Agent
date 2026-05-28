import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import math
import re
import json
import time

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# ===================================================
# Page config
# ===================================================
st.set_page_config(
    page_title="GF Festival Poster Agent",
    page_icon="🎨",
    layout="wide"
)


# ===================================================
# Holiday library
# ===================================================
HOLIDAY_LIBRARY = {
    "new_year": {
        "display_name": "元旦 / New Year",
        "colors": ["#C91616", "#FFFFFF", "#FFD68A"],
        "assets": ["firework", "light_beam", "circle_pattern"],
        "tone": "modern, festive, hopeful",
        "default_title": "元旦新禧",
        "default_subtitle": "HAPPY NEW YEAR",
        "default_blessing": "年首初月，歲如熹光。"
    },
    "spring_festival": {
        "display_name": "春节 / Chinese New Year",
        "colors": ["#B71919", "#FFD68A", "#FFF4E0"],
        "assets": ["lantern", "firework", "red_packet", "gold_coin", "gold_cloud"],
        "tone": "festive, warm, prosperous, corporate",
        "default_title": "恭賀新春",
        "default_subtitle": "廣發證券（香港）祝您新春快樂",
        "default_blessing": "馬到功成，財源廣進。"
    },
    "qingming": {
        "display_name": "清明节 / Ching Ming Festival",
        "colors": ["#EDEAE2", "#8A9A5B", "#333333"],
        "assets": ["mountain", "mist", "branch", "bird"],
        "tone": "calm, elegant, restrained",
        "default_title": "清明安康",
        "default_subtitle": "慎終追遠，春和景明",
        "default_blessing": "願您與家人平安順遂，萬事安康。"
    },
    "easter": {
        "display_name": "复活节 / Easter",
        "colors": ["#F7F3E8", "#D8A15D", "#6B7280"],
        "assets": ["soft_circle", "light_gradient"],
        "tone": "soft, clear, professional",
        "default_title": "Happy Easter",
        "default_subtitle": "復活節快樂",
        "default_blessing": "願春日暖意與美好祝福常伴您左右。"
    },
    "labour_day": {
        "display_name": "劳动节 / Labour Day",
        "colors": ["#C91616", "#FFD68A", "#FFF4E0"],
        "assets": ["gold_curve", "firework", "brand_symbol"],
        "tone": "energetic, positive, corporate",
        "default_title": "勞動節快樂",
        "default_subtitle": "致敬每一份努力與堅持",
        "default_blessing": "廣發證券（香港）祝您假期愉快，身心舒暢。"
    },
    "buddha_birthday": {
        "display_name": "佛诞 / Buddha's Birthday",
        "colors": ["#F3EFE2", "#D8A15D", "#333333"],
        "assets": ["sun", "cloud", "lotus_like_shape"],
        "tone": "peaceful, elegant, formal",
        "default_title": "佛誕吉祥",
        "default_subtitle": "廣發證券（香港）祝您佛誕安康",
        "default_blessing": "願心境澄明，福慧常伴，萬事順遂。"
    },
    "dragon_boat": {
        "display_name": "端午节 / Dragon Boat Festival",
        "colors": ["#0F766E", "#F2C16B", "#FFF8E7"],
        "assets": ["wave", "boat_shape", "gold_curve"],
        "tone": "traditional, energetic, festive",
        "default_title": "端午安康",
        "default_subtitle": "粽香盈袖，福至安康",
        "default_blessing": "廣發證券（香港）祝您端午安康。"
    },
    "hk_sar_day": {
        "display_name": "香港特别行政区成立纪念日 / HKSAR Establishment Day",
        "colors": ["#B71919", "#FFD68A", "#FFFFFF"],
        "assets": ["city_silhouette", "firework", "brand_symbol"],
        "tone": "formal, celebratory, civic",
        "default_title": "九州同慶\n盛世華誕",
        "default_subtitle": "香港特別行政區成立紀念日",
        "default_blessing": "同心同行，共啟新程。"
    },
    "mid_autumn": {
        "display_name": "中秋节 / Mid-Autumn Festival",
        "colors": ["#D99A3D", "#FFF2C6", "#7A4A12"],
        "assets": ["moon", "rabbit", "cloud", "branch", "water_reflection"],
        "tone": "warm, elegant, poetic, client-facing",
        "default_title": "情滿中秋\n月圓人團圓",
        "default_subtitle": "廣發證券（香港）祝您中秋快樂",
        "default_blessing": "月滿人團圓，佳節共安康。"
    },
    "national_day": {
        "display_name": "国庆日 / National Day",
        "colors": ["#B71919", "#FFD68A", "#FFF4E0"],
        "assets": ["firework", "gold_curve", "city_silhouette"],
        "tone": "grand, festive, formal",
        "default_title": "國慶快樂",
        "default_subtitle": "山河錦繡，盛世同慶",
        "default_blessing": "廣發證券（香港）祝您假期愉快。"
    },
    "chung_yeung": {
        "display_name": "重阳节 / Chung Yeung Festival",
        "colors": ["#F4F0E8", "#D99A4E", "#222222"],
        "assets": ["mountain", "sun", "ink_texture", "bird", "grass"],
        "tone": "traditional, calm, elegant",
        "default_title": "重陽安康",
        "default_subtitle": "登高望遠，秋意綿長",
        "default_blessing": "廣發證券（香港）祝您重陽安康，順遂如意。"
    },
    "thanksgiving": {
        "display_name": "感恩节 / Thanksgiving",
        "colors": ["#F5D06F", "#D99A3D", "#7A4A12"],
        "assets": ["warm_light", "thanksgiving_card", "gold_gradient"],
        "tone": "warm, grateful, client-facing",
        "default_title": "Thanksgiving",
        "default_subtitle": "感恩相伴",
        "default_blessing": "感謝一路同行，願溫暖與收穫常伴左右。"
    },
    "christmas": {
        "display_name": "圣诞节 / Christmas",
        "colors": ["#C91616", "#0C6B4E", "#FFD68A"],
        "assets": ["christmas_tree", "star", "snowflake", "gift"],
        "tone": "festive, joyful, warm",
        "default_title": "MERRY\nCHRISTMAS",
        "default_subtitle": "聖誕快樂",
        "default_blessing": "願節日的溫暖與喜悅常伴您左右。"
    }
}


# ===================================================
# Visual styles
# ===================================================
VISUAL_STYLE_LIBRARY = {
    "auto": "Auto based on holiday / 根据节日自动匹配",
    "ink_elegant": "水墨雅致",
    "red_gold": "红金节庆",
    "warm_gold": "暖金高级",
    "modern_brand": "现代品牌红"
}

ALLOWED_VISUAL_STYLES = ["ink_elegant", "red_gold", "warm_gold", "modern_brand"]


# ===================================================
# Multi-provider settings
# ===================================================
PROVIDER_LIBRARY = {
    "auto": {
        "display_name": "Auto / 自动选择可用 Provider",
        "api_key_name": None,
        "base_url_name": None,
        "model_name": None,
        "default_base_url": None,
        "default_model": None
    },
    "openrouter": {
        "display_name": "OpenRouter",
        "api_key_name": "OPENROUTER_API_KEY",
        "base_url_name": "OPENROUTER_BASE_URL",
        "model_name": "OPENROUTER_MODEL",
        "default_base_url": "https://openrouter.ai/api/v1",
        "default_model": "openrouter/free"
    },
    "groq": {
        "display_name": "Groq",
        "api_key_name": "GROQ_API_KEY",
        "base_url_name": "GROQ_BASE_URL",
        "model_name": "GROQ_MODEL",
        "default_base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-8b-instant"
    },
    "siliconflow": {
        "display_name": "SiliconFlow 硅基流动",
        "api_key_name": "SILICONFLOW_API_KEY",
        "base_url_name": "SILICONFLOW_BASE_URL",
        "model_name": "SILICONFLOW_MODEL",
        "default_base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-7B-Instruct"
    },
    "custom": {
        "display_name": "Custom OpenAI-compatible API",
        "api_key_name": "CUSTOM_API_KEY",
        "base_url_name": "CUSTOM_BASE_URL",
        "model_name": "CUSTOM_MODEL",
        "default_base_url": "",
        "default_model": ""
    }
}


# ===================================================
# Provider helpers
# ===================================================
def get_provider_config(provider_key):
    if provider_key not in PROVIDER_LIBRARY or provider_key == "auto":
        return None

    provider = PROVIDER_LIBRARY[provider_key]

    api_key = st.secrets.get(provider["api_key_name"], "")
    base_url = st.secrets.get(provider["base_url_name"], provider["default_base_url"])
    model = st.secrets.get(provider["model_name"], provider["default_model"])

    return {
        "provider_key": provider_key,
        "display_name": provider["display_name"],
        "api_key": api_key,
        "base_url": base_url,
        "model": model
    }


def get_configured_providers():
    configured = []

    for key in ["siliconflow", "groq", "openrouter", "custom"]:
        config = get_provider_config(key)

        if config and config["api_key"] and config["base_url"] and config["model"]:
            configured.append(key)

    return configured


def get_client(config):
    if OpenAI is None:
        return None

    if not config or not config["api_key"] or not config["base_url"]:
        return None

    return OpenAI(
        base_url=config["base_url"],
        api_key=config["api_key"]
    )


def extract_json(text):
    if not text:
        raise ValueError("Empty LLM response.")

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        return json.loads(match.group(0))

    raise ValueError("No valid JSON found in LLM response.")


def get_attempts(provider_choice, selected_model):
    attempts = []

    if provider_choice == "auto":
        for provider_key in get_configured_providers():
            config = get_provider_config(provider_key)
            attempts.append((provider_key, config["model"]))
        return attempts

    config = get_provider_config(provider_choice)

    if config:
        model = selected_model.strip() if selected_model and selected_model.strip() else config["model"]
        attempts.append((provider_choice, model))

    return attempts


def call_llm_json(messages, provider_choice, selected_model):
    attempts = get_attempts(provider_choice, selected_model)

    if not attempts:
        return None

    for provider_key, model in attempts:
        config = get_provider_config(provider_key)
        client = get_client(config)

        if client is None:
            continue

        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.35,
                "max_tokens": 700
            }

            if provider_key == "openrouter":
                kwargs["extra_headers"] = {
                    "HTTP-Referer": "https://streamlit.app",
                    "X-Title": "GF Festival Poster Agent"
                }

            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            return extract_json(content)

        except Exception as e:
            error_text = str(e)

            if (
                "429" in error_text
                or "rate limit" in error_text.lower()
                or "rate-limited" in error_text.lower()
            ):
                st.warning(f"{config['display_name']} is temporarily rate-limited. Trying another provider...")
                time.sleep(1)
                continue

            if "No endpoints found" in error_text or "404" in error_text:
                st.warning(f"{config['display_name']} model endpoint unavailable. Trying another provider...")
                continue

            st.warning(f"{config['display_name']} failed. Falling back if possible.")
            continue

    return None


# ===================================================
# Font loading
# ===================================================
def load_font(size, bold=False):
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
# General helpers
# ===================================================
def image_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def add_noise_texture(img, opacity=10):
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


def normalize_text(text):
    text = text.lower().strip()

    replacements = {
        "節": "节",
        "誕": "诞",
        "聖": "圣",
        "國": "国",
        "陽": "阳",
        "龍": "龙",
        "勞": "劳",
        "動": "动",
        "復": "复",
        "農": "农",
        "曆": "历",
        "慶": "庆",
        "樂": "乐",
        "廣": "广",
        "證": "证"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace("-", " ")
    text = re.sub(r"\s+", " ", text)

    return text


def clamp_text(value, max_len):
    if value is None:
        return ""
    return str(value).strip()[:max_len]


def sanitize_assets(assets, holiday_key):
    allowed = HOLIDAY_LIBRARY[holiday_key]["assets"]

    if not isinstance(assets, list):
        return allowed

    selected = [a for a in assets if a in allowed]

    return selected if selected else allowed


def resolve_visual_style(holiday_key, visual_style_choice):
    if visual_style_choice != "auto":
        return visual_style_choice

    if holiday_key in ["chung_yeung", "qingming", "buddha_birthday"]:
        return "ink_elegant"

    if holiday_key in ["spring_festival", "national_day", "hk_sar_day"]:
        return "red_gold"

    if holiday_key in ["mid_autumn", "thanksgiving", "dragon_boat"]:
        return "warm_gold"

    if holiday_key in ["christmas", "new_year", "labour_day"]:
        return "modern_brand"

    return "red_gold"


# ===================================================
# Drawing assets
# ===================================================
def draw_company_brand(draw, x, y, color="#B8A06A", scale=1.0):
    logo_font = load_font(int(40 * scale), bold=True)
    sub_font = load_font(int(17 * scale), bold=False)

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
    draw.rectangle([x + 20, y + h - 5, x + w - 20, y + h + 10], fill=gold)
    draw.line([x + w // 2, y + h + 10, x + w // 2, y + h + 45], fill=gold, width=2)


def draw_moon_scene(draw, width, height):
    draw.ellipse([190, 360, 710, 880], fill="#FFF4C8")
    draw.ellipse([235, 405, 665, 835], fill="#FBE7A5")

    draw.ellipse([430, 650, 620, 720], fill="#FFF9D8")
    draw.ellipse([540, 625, 720, 705], fill="#FFF9D8")
    draw.rectangle([430, 670, 720, 720], fill="#FFF9D8")

    for i in range(5):
        draw.line([60, 410 + i * 30, 300, 320 + i * 20], fill="#8A5A20", width=4)

    draw.ellipse([385, 735, 535, 880], fill="#DFAE45")
    draw.ellipse([430, 690, 470, 770], fill="#DFAE45")
    draw.ellipse([475, 690, 515, 770], fill="#DFAE45")

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


def draw_red_packet_scene(draw, width, height):
    draw.rounded_rectangle([250, 520, 650, 870], radius=32, fill="#FCE6B0")
    draw.rounded_rectangle([300, 570, 600, 830], radius=22, fill="#D92020")
    draw.ellipse([390, 640, 520, 770], fill="#F7B15A")


def draw_modern_geometry(draw, width, height, color="#E85A3C"):
    draw.polygon([(0, 300), (width, 160), (width, 520), (0, 620)], fill=color)
    draw.polygon([(210, 360), (560, 260), (350, 1220), (0, 1220)], fill="#A80F0F")
    draw.ellipse([520, 660, 950, 1090], fill="#E46B3E")
    draw.ellipse([610, 750, 850, 990], fill="#C91616")


def draw_wave_scene(draw, width, height):
    for i in range(7):
        y = 670 + i * 28
        draw.arc([80 - i * 20, y, width - 80 + i * 20, y + 90], 180, 360, fill="#F2C16B", width=4)

    draw.polygon([(260, 550), (620, 550), (540, 640), (330, 640)], fill="#0F766E")


def draw_soft_light_scene(draw, width, height):
    for radius, color in [(560, "#F7E7A8"), (430, "#F5D06F"), (300, "#D99A3D")]:
        x1 = width // 2 - radius // 2
        y1 = 430 - radius // 2
        x2 = width // 2 + radius // 2
        y2 = 430 + radius // 2
        draw.ellipse([x1, y1, x2, y2], fill=color)


def draw_lotus_like_shape(draw, width, height):
    cx, cy = width // 2, 760
    petal_color = "#E2B46A"

    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + int(math.cos(angle) * 90)
        y = cy + int(math.sin(angle) * 45)
        draw.ellipse([x - 70, y - 35, x + 70, y + 35], fill=petal_color)

    draw.ellipse([cx - 90, cy - 45, cx + 90, cy + 45], fill="#F7E7A8")


def draw_city_silhouette(draw, width, height, color="#8A0F0F"):
    base_y = 1000
    buildings = [
        (90, base_y - 180, 150, base_y),
        (170, base_y - 280, 240, base_y),
        (270, base_y - 220, 340, base_y),
        (650, base_y - 330, 730, base_y),
        (760, base_y - 210, 830, base_y)
    ]

    for x1, y1, x2, y2 in buildings:
        draw.rectangle([x1, y1, x2, y2], fill=color)


def draw_qr_placeholder(draw, width, height):
    draw.rounded_rectangle(
        [700, height - 170, 820, height - 50],
        radius=12,
        outline="#D8D8D8",
        width=3
    )
    draw.text((705, height - 25), "QR reserved", fill="#999999", font=load_font(18))


# ===================================================
# Poster state generation
# ===================================================
def generate_base_state(holiday_key, visual_style_choice):
    holiday = HOLIDAY_LIBRARY[holiday_key]
    visual_style = resolve_visual_style(holiday_key, visual_style_choice)

    return {
        "poster_type": "festival_greeting",
        "holiday_key": holiday_key,
        "holiday_name": holiday["display_name"],
        "visual_style": visual_style,
        "colors": holiday["colors"],
        "selected_assets": holiday["assets"],
        "tone": holiday["tone"],
        "title": holiday["default_title"],
        "subtitle": holiday["default_subtitle"],
        "blessing": holiday["default_blessing"]
    }


def enhance_state_with_llm(state, user_prompt, provider_choice, selected_model):
    holiday_key = state["holiday_key"]
    allowed_assets = HOLIDAY_LIBRARY[holiday_key]["assets"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional corporate festival poster copywriter. "
                "Return ONLY valid JSON. Do not use markdown. "
                "Use Traditional Chinese for Chinese output. "
                "Keep text concise for poster layout. "
                "Do not invent visual assets. selected_assets must only use allowed assets. "
                "Avoid cheesy internet language and exaggerated sales tone."
            )
        },
        {
            "role": "user",
            "content": json.dumps({
                "task": "Generate refined poster text and controlled visual choices.",
                "user_prompt": user_prompt,
                "current_state": state,
                "allowed_assets": allowed_assets,
                "allowed_visual_styles": ALLOWED_VISUAL_STYLES,
                "output_json_keys": ["title", "subtitle", "blessing", "visual_style", "selected_assets"],
                "constraints": [
                    "Do not change poster_type.",
                    "Do not change holiday_key.",
                    "Do not change holiday_name.",
                    "Use Traditional Chinese unless the title is naturally English, such as Christmas or Thanksgiving.",
                    "Keep title short.",
                    "Keep subtitle short.",
                    "Keep blessing as one concise client-facing sentence."
                ]
            }, ensure_ascii=False)
        }
    ]

    llm_data = call_llm_json(messages, provider_choice, selected_model)

    if not llm_data:
        return state

    state["title"] = clamp_text(llm_data.get("title", state["title"]), 34)
    state["subtitle"] = clamp_text(llm_data.get("subtitle", state["subtitle"]), 48)
    state["blessing"] = clamp_text(llm_data.get("blessing", state["blessing"]), 72)

    if llm_data.get("visual_style") in ALLOWED_VISUAL_STYLES:
        state["visual_style"] = llm_data["visual_style"]

    state["selected_assets"] = sanitize_assets(
        llm_data.get("selected_assets", state["selected_assets"]),
        holiday_key
    )

    return state


def generate_poster_state(holiday_key, visual_style_choice, user_prompt, use_llm, provider_choice, selected_model):
    state = generate_base_state(holiday_key, visual_style_choice)

    if use_llm:
        state = enhance_state_with_llm(state, user_prompt, provider_choice, selected_model)

    return state


# ===================================================
# Revision
# ===================================================
def rule_based_revise_state(state, revision_prompt):
    updated = state.copy()
    r = normalize_text(revision_prompt)

    if "正式" in r or "formal" in r:
        updated["subtitle"] = "廣發證券（香港）謹祝您節日愉快"
        updated["blessing"] = "願您與家人平安順遂，萬事如意。"

    if "简短" in r or "简单" in r or "short" in r:
        updated["blessing"] = "佳節愉快，萬事順遂。"

    if "温暖" in r or "暖" in r or "warm" in r:
        updated["blessing"] = "願這份節日暖意，伴您與家人共度美好時光。"

    if "不要快乐" in r or "不要快樂" in r:
        updated["subtitle"] = updated["subtitle"].replace("快樂", "安康").replace("快乐", "安康")
        updated["blessing"] = updated["blessing"].replace("快樂", "安康").replace("快乐", "安康")

    if "水墨" in r:
        updated["visual_style"] = "ink_elegant"

    if "红金" in r or "喜庆" in r:
        updated["visual_style"] = "red_gold"

    if "暖金" in r or "高级" in r:
        updated["visual_style"] = "warm_gold"

    if "现代" in r or "品牌" in r:
        updated["visual_style"] = "modern_brand"

    return updated


def revise_state_with_llm(state, revision_prompt, provider_choice, selected_model):
    holiday_key = state["holiday_key"]
    allowed_assets = HOLIDAY_LIBRARY[holiday_key]["assets"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional poster revision assistant. "
                "Return ONLY valid JSON. Do not use markdown. "
                "Use Traditional Chinese for Chinese text. "
                "Update only what the user asks to change. "
                "Do not invent visual assets."
            )
        },
        {
            "role": "user",
            "content": json.dumps({
                "current_state": state,
                "revision_instruction": revision_prompt,
                "allowed_visual_styles": ALLOWED_VISUAL_STYLES,
                "allowed_assets": allowed_assets,
                "output_requirements": [
                    "Return complete updated poster_state JSON.",
                    "You may update title, subtitle, blessing, visual_style, selected_assets.",
                    "Do not change poster_type, holiday_key, holiday_name, colors, or tone.",
                    "selected_assets must only use allowed_assets."
                ]
            }, ensure_ascii=False)
        }
    ]

    llm_data = call_llm_json(messages, provider_choice, selected_model)

    if not llm_data:
        return rule_based_revise_state(state, revision_prompt)

    updated = state.copy()

    for key in ["title", "subtitle", "blessing"]:
        if key in llm_data:
            updated[key] = clamp_text(llm_data[key], 72)

    if llm_data.get("visual_style") in ALLOWED_VISUAL_STYLES:
        updated["visual_style"] = llm_data["visual_style"]

    if "selected_assets" in llm_data:
        updated["selected_assets"] = sanitize_assets(llm_data["selected_assets"], holiday_key)

    return updated


# ===================================================
# Renderer
# ===================================================
def render_festival_greeting(state, reserve_qr=True):
    width, height = 900, 1600
    colors = state["colors"]
    bg = colors[0]
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

    if visual_style == "warm_gold" or "moon" in assets:
        draw_moon_scene(draw, width, height)

    elif visual_style == "modern_brand":
        draw_modern_geometry(draw, width, height)

        if "firework" in assets:
            draw_firework(draw, 210, 1050, 90, "#FFF1C4")
            draw_firework(draw, 710, 680, 70, "#FFF1C4")

    elif visual_style == "ink_elegant":
        if "lotus_like_shape" in assets:
            draw_soft_light_scene(draw, width, height)
            draw_lotus_like_shape(draw, width, height)
        else:
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

    if "christmas_tree" in assets:
        draw_christmas_tree(draw, width // 2, 620)

    if "city_silhouette" in assets:
        draw_city_silhouette(draw, width, height)

    if "wave" in assets:
        draw_wave_scene(draw, width, height)

    brand_color = "#E4D0A1" if bg.lower() != "#f4f0e8" else "#B8A06A"
    draw_company_brand(draw, 70, 70, color=brand_color, scale=0.7)

    title_lines = state["title"].split("\n")
    title_y = 260

    for line in title_lines:
        font = big_font if len(line) <= 6 else title_font
        draw_centered_text(draw, line, title_y, font, text_color, width)
        title_y += font.size + 18

    draw_centered_text(draw, state["subtitle"], title_y + 40, subtitle_font, text_color, width)
    draw_centered_text(draw, state["blessing"], title_y + 105, body_font, text_color, width)

    if "red_packet" in assets and holiday_key == "spring_festival":
        draw.text((270, 1010), "恭 賀 新 春", fill=text_color, font=load_font(60, bold=True))

    if "light_beam" in assets:
        draw.line([450, 340, 450, 760], fill="#FFF6DA", width=12)
        draw.ellipse([405, 240, 495, 330], fill="#FFF6DA")

    draw.pieslice([-160, height - 350, width + 160, height + 220], 180, 360, fill="#FFFFFF")
    draw_company_brand(draw, 70, height - 150, color="#B8A06A", scale=0.75)

    if reserve_qr:
        draw_qr_placeholder(draw, width, height)

    return img


# ===================================================
# Streamlit UI
# ===================================================
st.title("🎨 GF Securities Festival Poster Agent")
st.write("Generate company-style festival greeting posters with controlled assets and optional LLM copywriting.")

with st.sidebar:
    st.header("Poster Settings")

    holiday_key = st.selectbox(
        "节日主题 / Holiday Theme",
        options=list(HOLIDAY_LIBRARY.keys()),
        index=list(HOLIDAY_LIBRARY.keys()).index("mid_autumn"),
        format_func=lambda x: HOLIDAY_LIBRARY[x]["display_name"]
    )

    visual_style_choice = st.selectbox(
        "视觉风格 / Visual Style",
        options=list(VISUAL_STYLE_LIBRARY.keys()),
        format_func=lambda x: VISUAL_STYLE_LIBRARY[x]
    )

    reserve_qr = st.checkbox("Reserve QR area / 预留二维码位置", value=True)

    st.divider()

    st.header("AI Provider")

    use_llm = st.toggle("Use LLM for copywriting", value=True)

    provider_choice = st.selectbox(
        "Provider",
        options=list(PROVIDER_LIBRARY.keys()),
        format_func=lambda x: PROVIDER_LIBRARY[x]["display_name"]
    )

    default_model = ""
    if provider_choice != "auto":
        config = get_provider_config(provider_choice)
        default_model = config["model"] if config else ""

    selected_model = st.text_input(
        "Model",
        value=default_model,
        placeholder="Leave empty to use model from Secrets"
    )

    show_debug = st.checkbox("Show debug JSON", value=False)

    configured = get_configured_providers()

    if use_llm:
        if provider_choice == "auto":
            if configured:
                names = [PROVIDER_LIBRARY[p]["display_name"] for p in configured]
                st.success("Configured: " + ", ".join(names))
            else:
                st.warning("No provider configured in Secrets.")
        else:
            config = get_provider_config(provider_choice)
            if config and config["api_key"] and config["base_url"] and (selected_model or config["model"]):
                st.success(f"{config['display_name']} configured")
            else:
                st.warning("Selected provider is not fully configured.")

st.divider()

# ===================================================
# Generate poster
# ===================================================
st.subheader("1. Generate Poster")

default_prompt = "面向客户，语气正式温暖，文案不要太俗套，保留节日氛围。"

user_prompt = st.text_area(
    "输入文案要求 / Copywriting instruction",
    value=default_prompt,
    height=120
)

if st.button("Generate Poster"):
    if not user_prompt.strip():
        st.warning("Please enter a copywriting instruction.")
    else:
        with st.spinner("Generating poster..."):
            state = generate_poster_state(
                holiday_key=holiday_key,
                visual_style_choice=visual_style_choice,
                user_prompt=user_prompt,
                use_llm=use_llm,
                provider_choice=provider_choice,
                selected_model=selected_model
            )

            st.session_state["poster_state"] = state
            poster = render_festival_greeting(state, reserve_qr=reserve_qr)
            st.session_state["poster"] = poster

        st.success("Poster generated.")

        col1, col2 = st.columns([1.25, 1])

        with col1:
            st.image(poster, caption="Generated Poster Preview", use_container_width=False)

            st.download_button(
                label="Download Poster as PNG",
                data=image_to_bytes(poster),
                file_name="gf_festival_poster.png",
                mime="image/png"
            )

        with col2:
            st.subheader("Generation Summary")
            st.write(f"**Holiday:** {state['holiday_name']}")
            st.write(f"**Visual style:** {VISUAL_STYLE_LIBRARY.get(state['visual_style'], state['visual_style'])}")
            st.write(f"**Selected assets:** {', '.join(state['selected_assets'])}")

            if show_debug:
                st.subheader("Debug JSON")
                st.json(state)

st.divider()

# ===================================================
# Revise poster
# ===================================================
st.subheader("2. Revise Poster")

revision_prompt = st.text_area(
    "输入修改指令 / Revision instruction",
    placeholder="例如：文案更正式一点 / 不要出现快乐 / 保留风格，只改祝福语 / 改成更高级的语气",
    height=100
)

if st.button("Apply Revision"):
    if "poster_state" not in st.session_state:
        st.warning("Please generate a poster first.")
    elif not revision_prompt.strip():
        st.warning("Please enter a revision instruction.")
    else:
        with st.spinner("Applying revision..."):
            if use_llm:
                updated_state = revise_state_with_llm(
                    state=st.session_state["poster_state"],
                    revision_prompt=revision_prompt,
                    provider_choice=provider_choice,
                    selected_model=selected_model
                )
            else:
                updated_state = rule_based_revise_state(
                    st.session_state["poster_state"],
                    revision_prompt
                )

            st.session_state["poster_state"] = updated_state
            poster = render_festival_greeting(updated_state, reserve_qr=reserve_qr)
            st.session_state["poster"] = poster

        st.success("Revision applied.")

        col1, col2 = st.columns([1.25, 1])

        with col1:
            st.image(poster, caption="Revised Poster Preview", use_container_width=False)

            st.download_button(
                label="Download Revised Poster as PNG",
                data=image_to_bytes(poster),
                file_name="gf_festival_poster_revised.png",
                mime="image/png"
            )

        with col2:
            st.subheader("Revision Summary")
            st.write(f"**Holiday:** {updated_state['holiday_name']}")
            st.write(f"**Visual style:** {VISUAL_STYLE_LIBRARY.get(updated_state['visual_style'], updated_state['visual_style'])}")
            st.write(f"**Selected assets:** {', '.join(updated_state['selected_assets'])}")

            if show_debug:
                st.subheader("Debug JSON")
                st.json(updated_state)

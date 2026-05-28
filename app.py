import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json
import re
import math
import random

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# =========================================================
# Page config
# =========================================================
st.set_page_config(
    page_title="GF Festival Poster Agent",
    page_icon="🎨",
    layout="wide"
)


# =========================================================
# Holiday config
# =========================================================
HOLIDAYS = {
    "new_year": {
        "name": "元旦 / New Year",
        "title": "元旦新禧",
        "subtitle": "HAPPY NEW YEAR",
        "blessing": "年首初月，歲如熹光。",
        "colors": ["#C91616", "#FFF4D6", "#FFD68A"],
        "assets": ["firework", "light_beam", "circle"],
        "style": "modern_brand",
    },
    "spring_festival": {
        "name": "春节 / Chinese New Year",
        "title": "恭賀新春",
        "subtitle": "廣發證券（香港）祝您新春快樂",
        "blessing": "馬到功成，財源廣進。",
        "colors": ["#B71919", "#FFF4D6", "#FFD68A"],
        "assets": ["lantern", "firework", "red_packet"],
        "style": "red_gold",
    },
    "qingming": {
        "name": "清明节 / Ching Ming Festival",
        "title": "清明安康",
        "subtitle": "慎終追遠，春和景明",
        "blessing": "願您與家人平安順遂，萬事安康。",
        "colors": ["#F4F0E8", "#222222", "#D99A4E"],
        "assets": ["mountain", "sun", "branch"],
        "style": "ink_elegant",
    },
    "easter": {
        "name": "复活节 / Easter",
        "title": "Happy Easter",
        "subtitle": "復活節快樂",
        "blessing": "願春日暖意與美好祝福常伴您左右。",
        "colors": ["#F7F3E8", "#333333", "#D8A15D"],
        "assets": ["soft_circle", "light_gradient"],
        "style": "ink_elegant",
    },
    "labour_day": {
        "name": "劳动节 / Labour Day",
        "title": "勞動節快樂",
        "subtitle": "致敬每一份努力與堅持",
        "blessing": "廣發證券（香港）祝您假期愉快，身心舒暢。",
        "colors": ["#C91616", "#FFF4D6", "#FFD68A"],
        "assets": ["firework", "gold_curve"],
        "style": "modern_brand",
    },
    "buddha_birthday": {
        "name": "佛诞 / Buddha's Birthday",
        "title": "佛誕吉祥",
        "subtitle": "廣發證券（香港）祝您佛誕安康",
        "blessing": "願心境澄明，福慧常伴，萬事順遂。",
        "colors": ["#F3EFE2", "#222222", "#D8A15D"],
        "assets": ["sun", "cloud", "lotus"],
        "style": "ink_elegant",
    },
    "dragon_boat": {
        "name": "端午节 / Dragon Boat Festival",
        "title": "端午安康",
        "subtitle": "粽香盈袖，福至安康",
        "blessing": "廣發證券（香港）祝您端午安康。",
        "colors": ["#0F766E", "#FFF8E7", "#F2C16B"],
        "assets": ["wave", "boat"],
        "style": "warm_gold",
    },
    "hk_sar_day": {
        "name": "香港特别行政区成立纪念日 / HKSAR Establishment Day",
        "title": "九州同慶\n盛世華誕",
        "subtitle": "香港特別行政區成立紀念日",
        "blessing": "同心同行，共啟新程。",
        "colors": ["#B71919", "#FFF4D6", "#FFD68A"],
        "assets": ["city", "firework"],
        "style": "red_gold",
    },
    "mid_autumn": {
        "name": "中秋节 / Mid-Autumn Festival",
        "title": "情滿中秋\n月圓人團圓",
        "subtitle": "廣發證券（香港）祝您中秋快樂",
        "blessing": "月滿人團圓，佳節共安康。",
        "colors": ["#D99A3D", "#7A4A12", "#FFF2C6"],
        "assets": ["moon", "rabbit", "cloud", "branch"],
        "style": "warm_gold",
    },
    "national_day": {
        "name": "国庆日 / National Day",
        "title": "國慶快樂",
        "subtitle": "山河錦繡，盛世同慶",
        "blessing": "廣發證券（香港）祝您假期愉快。",
        "colors": ["#B71919", "#FFF4D6", "#FFD68A"],
        "assets": ["firework", "city"],
        "style": "red_gold",
    },
    "chung_yeung": {
        "name": "重阳节 / Chung Yeung Festival",
        "title": "重陽安康",
        "subtitle": "登高望遠，秋意綿長",
        "blessing": "廣發證券（香港）祝您重陽安康，順遂如意。",
        "colors": ["#F4F0E8", "#222222", "#D99A4E"],
        "assets": ["mountain", "sun", "branch"],
        "style": "ink_elegant",
    },
    "thanksgiving": {
        "name": "感恩节 / Thanksgiving",
        "title": "Thanksgiving",
        "subtitle": "感恩相伴",
        "blessing": "感謝一路同行，願溫暖與收穫常伴左右。",
        "colors": ["#F5D06F", "#7A4A12", "#D99A3D"],
        "assets": ["warm_light", "gold_gradient"],
        "style": "warm_gold",
    },
    "christmas": {
        "name": "圣诞节 / Christmas",
        "title": "MERRY\nCHRISTMAS",
        "subtitle": "聖誕快樂",
        "blessing": "願節日的溫暖與喜悅常伴您左右。",
        "colors": ["#C91616", "#FFF4D6", "#0C6B4E"],
        "assets": ["christmas_tree", "snowflake", "star"],
        "style": "modern_brand",
    },
}


VISUAL_STYLES = {
    "auto": "Auto based on holiday / 根据节日自动匹配",
    "red_gold": "红金节庆",
    "warm_gold": "暖金高级",
    "ink_elegant": "水墨雅致",
    "modern_brand": "现代品牌红",
}


PROVIDERS = {
    "openrouter": {
        "label": "OpenRouter",
        "api_key": "OPENROUTER_API_KEY",
        "base_url": "OPENROUTER_BASE_URL",
        "model": "OPENROUTER_MODEL",
        "default_base_url": "https://openrouter.ai/api/v1",
        "default_model": "openrouter/free",
    },
    "groq": {
        "label": "Groq",
        "api_key": "GROQ_API_KEY",
        "base_url": "GROQ_BASE_URL",
        "model": "GROQ_MODEL",
        "default_base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-8b-instant",
    },
    "siliconflow": {
        "label": "SiliconFlow 硅基流动",
        "api_key": "SILICONFLOW_API_KEY",
        "base_url": "SILICONFLOW_BASE_URL",
        "model": "SILICONFLOW_MODEL",
        "default_base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
    },
    "custom": {
        "label": "Custom OpenAI-compatible API",
        "api_key": "CUSTOM_API_KEY",
        "base_url": "CUSTOM_BASE_URL",
        "model": "CUSTOM_MODEL",
        "default_base_url": "",
        "default_model": "",
    },
}


# =========================================================
# Secrets / Provider helpers
# =========================================================
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def mask_key(key):
    if not key:
        return "Not found"
    if len(key) < 10:
        return "***"
    return key[:5] + "..." + key[-4:]


def get_provider_config(provider_key, model_override=""):
    p = PROVIDERS[provider_key]

    api_key = get_secret(p["api_key"], "")
    base_url = get_secret(p["base_url"], p["default_base_url"])
    model = model_override.strip() if model_override.strip() else get_secret(p["model"], p["default_model"])

    return {
        "key": provider_key,
        "label": p["label"],
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def get_available_providers():
    available = []
    for key in PROVIDERS:
        cfg = get_provider_config(key)
        if cfg["api_key"] and cfg["base_url"] and cfg["model"]:
            available.append(key)
    return available


def parse_json_from_text(text):
    if not text:
        raise ValueError("Empty response from model.")

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in model response: {text[:500]}")

    return json.loads(match.group(0))


def call_llm_json(messages, provider_key, model_override="", show_debug=True):
    if OpenAI is None:
        st.error("openai package is not installed. Please add `openai` to requirements.txt.")
        return None

    provider_attempts = []

    if provider_key == "auto":
        provider_attempts = get_available_providers()
    else:
        provider_attempts = [provider_key]

    if not provider_attempts:
        st.error("No API provider configured. Please add API key and model in Streamlit Secrets.")
        return None

    for key in provider_attempts:
        cfg = get_provider_config(key, model_override)

        if not cfg["api_key"] or not cfg["base_url"] or not cfg["model"]:
            st.error(
                f"{cfg['label']} is not fully configured.\n\n"
                f"API key: {mask_key(cfg['api_key'])}\n\n"
                f"Base URL: {cfg['base_url']}\n\n"
                f"Model: {cfg['model']}"
            )
            continue

        try:
            client = OpenAI(
                base_url=cfg["base_url"],
                api_key=cfg["api_key"],
            )

            kwargs = {
                "model": cfg["model"],
                "messages": messages,
                "temperature": 0.35,
                "max_tokens": 700,
            }

            if key == "openrouter":
                kwargs["extra_headers"] = {
                    "HTTP-Referer": "https://streamlit.app",
                    "X-Title": "GF Festival Poster Agent",
                }

            if show_debug:
                st.info(
                    f"Trying {cfg['label']} | "
                    f"model: {cfg['model']} | "
                    f"base_url: {cfg['base_url']} | "
                    f"api_key: {mask_key(cfg['api_key'])}"
                )

            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            if show_debug:
                st.success(f"LLM call succeeded: {cfg['label']}")

            return parse_json_from_text(content)

        except Exception as e:
            st.error(
                f"LLM call failed.\n\n"
                f"Provider: {cfg['label']}\n\n"
                f"Model: {cfg['model']}\n\n"
                f"Base URL: {cfg['base_url']}\n\n"
                f"API Key: {mask_key(cfg['api_key'])}\n\n"
                f"Error: {str(e)}"
            )

    return None


# =========================================================
# Fonts
# =========================================================
def load_font(size, bold=False):
    paths = []

    if bold:
        paths.extend([
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        ])

    paths.extend([
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ])

    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue

    return ImageFont.load_default()


# =========================================================
# Image helpers
# =========================================================
def image_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def centered_text(draw, text, y, font, fill, width):
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)


def add_noise(img, opacity=8):
    w, h = img.size
    noise = Image.new("RGB", (w, h), "#FFFFFF")
    pix = noise.load()

    for x in range(w):
        for y in range(h):
            v = random.randint(230, 255)
            pix[x, y] = (v, v, v)

    return Image.blend(img, noise, opacity / 255)


# =========================================================
# Drawing elements
# =========================================================
def draw_brand(draw, x, y, color="#B8A06A", scale=1.0):
    name_font = load_font(int(38 * scale), bold=True)
    en_font = load_font(int(16 * scale), bold=False)

    draw.rounded_rectangle(
        [x, y + int(8 * scale), x + int(68 * scale), y + int(48 * scale)],
        radius=int(14 * scale),
        outline=color,
        width=max(2, int(5 * scale))
    )

    draw.text((x + int(85 * scale), y), "廣發證券（香港）", font=name_font, fill=color)
    draw.text((x + int(87 * scale), y + int(50 * scale)), "GF SECURITIES (HONG KONG)", font=en_font, fill=color)


def draw_firework(draw, cx, cy, r, color="#FFD68A"):
    for i in range(20):
        angle = 2 * math.pi * i / 20
        x1 = cx + math.cos(angle) * r * 0.25
        y1 = cy + math.sin(angle) * r * 0.25
        x2 = cx + math.cos(angle) * r
        y2 = cy + math.sin(angle) * r
        draw.line([x1, y1, x2, y2], fill=color, width=3)


def draw_lantern(draw, x, y, scale=1.0):
    w = int(70 * scale)
    h = int(110 * scale)
    draw.line([x + w // 2, y - 35, x + w // 2, y], fill="#FFD68A", width=3)
    draw.ellipse([x, y, x + w, y + h], fill="#D7261E", outline="#FFD68A", width=3)
    draw.rectangle([x + 20, y + h - 5, x + w - 20, y + h + 10], fill="#FFD68A")
    draw.line([x + w // 2, y + h + 10, x + w // 2, y + h + 45], fill="#FFD68A", width=2)


def draw_moon_scene(draw, width, height):
    draw.ellipse([190, 350, 710, 870], fill="#FFF4C8")
    draw.ellipse([250, 410, 650, 810], fill="#FBE7A5")

    draw.ellipse([430, 640, 610, 715], fill="#FFF9D8")
    draw.ellipse([535, 620, 710, 705], fill="#FFF9D8")
    draw.rectangle([430, 670, 710, 720], fill="#FFF9D8")

    for i in range(5):
        draw.line([70, 410 + i * 30, 300, 320 + i * 20], fill="#8A5A20", width=4)

    draw.ellipse([385, 735, 535, 880], fill="#DFAE45")
    draw.ellipse([430, 690, 470, 770], fill="#DFAE45")
    draw.ellipse([475, 690, 515, 770], fill="#DFAE45")


def draw_mountain_scene(draw, width, height):
    draw.ellipse([610, 220, 790, 400], fill="#E7A15F")
    draw.polygon([(0, 430), (130, 330), (250, 440)], fill="#D8D8D8")
    draw.polygon([(620, 520), (760, 410), (930, 520)], fill="#D0D0D0")
    draw.polygon([(360, 500), (520, 410), (690, 510)], fill="#E1E1E1")

    for i in range(6):
        x = 40 + i * 20
        draw.arc([x, 520 - i * 8, x + 180, 760], 210, 285, fill="#C8B27D", width=2)


def draw_christmas_tree(draw, cx, cy):
    draw_firework(draw, cx, cy - 30, 35, "#FFD68A")
    draw.polygon([(cx, cy), (cx - 170, cy + 260), (cx + 170, cy + 260)], fill="#0C6B4E")
    draw.polygon([(cx, cy + 160), (cx - 215, cy + 460), (cx + 215, cy + 460)], fill="#0C6B4E")
    draw.rectangle([cx - 36, cy + 460, cx + 36, cy + 575], fill="#0C6B4E")


def draw_red_packet(draw, width, height):
    draw.rounded_rectangle([250, 520, 650, 870], radius=32, fill="#FCE6B0")
    draw.rounded_rectangle([300, 570, 600, 830], radius=22, fill="#D92020")
    draw.ellipse([390, 640, 520, 770], fill="#F7B15A")


def draw_modern_geometry(draw, width, height):
    draw.polygon([(0, 300), (width, 160), (width, 520), (0, 620)], fill="#E85A3C")
    draw.polygon([(210, 360), (560, 260), (350, 1220), (0, 1220)], fill="#A80F0F")
    draw.ellipse([520, 660, 950, 1090], fill="#E46B3E")


def draw_city(draw, width, height):
    base_y = 1000
    for x1, y1, x2, y2 in [
        (90, base_y - 180, 150, base_y),
        (170, base_y - 280, 240, base_y),
        (270, base_y - 220, 340, base_y),
        (650, base_y - 330, 730, base_y),
        (760, base_y - 210, 830, base_y),
    ]:
        draw.rectangle([x1, y1, x2, y2], fill="#8A0F0F")


def draw_wave(draw, width, height):
    for i in range(7):
        y = 670 + i * 28
        draw.arc([80 - i * 20, y, width - 80 + i * 20, y + 90], 180, 360, fill="#F2C16B", width=4)


def draw_lotus(draw, width, height):
    cx, cy = width // 2, 760
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + int(math.cos(angle) * 90)
        y = cy + int(math.sin(angle) * 45)
        draw.ellipse([x - 70, y - 35, x + 70, y + 35], fill="#E2B46A")
    draw.ellipse([cx - 90, cy - 45, cx + 90, cy + 45], fill="#F7E7A8")


def draw_qr_placeholder(draw, width, height):
    draw.rounded_rectangle([700, height - 170, 820, height - 50], radius=12, outline="#D8D8D8", width=3)
    draw.text((705, height - 25), "QR reserved", fill="#999999", font=load_font(18))


# =========================================================
# State generation
# =========================================================
def resolve_style(holiday_key, visual_style):
    if visual_style != "auto":
        return visual_style

    holiday = HOLIDAYS.get(holiday_key, HOLIDAYS["mid_autumn"])

    return holiday.get("style", "warm_gold")


def generate_base_state(holiday_key, visual_style):
    holiday = HOLIDAYS.get(holiday_key, HOLIDAYS["mid_autumn"])

    return {
        "holiday_key": holiday_key,
        "holiday_name": holiday.get("name", "節日"),
        "title": holiday.get("title", "節日快樂"),
        "subtitle": holiday.get("subtitle", "廣發證券（香港）祝您節日愉快"),
        "blessing": holiday.get("blessing", "願您與家人平安順遂，萬事如意。"),
        "colors": holiday.get("colors", ["#D99A3D", "#7A4A12", "#FFF2C6"]),
        "selected_assets": holiday.get("assets", []),
        "visual_style": resolve_style(holiday_key, visual_style),
        "tone": holiday.get("tone", "professional, warm, client-facing"),
    }

def generate_state_with_llm(state, user_prompt, provider_key, model_override):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional corporate festival poster copywriter. "
                "Return ONLY valid JSON. No markdown. "
                "Use Traditional Chinese. "
                "Keep all text concise. "
                "Do not invent visual assets."
            )
        },
        {
            "role": "user",
            "content": json.dumps({
                "current_state": state,
                "user_prompt": user_prompt,
                "allowed_visual_styles": list(VISUAL_STYLES.keys()),
                "allowed_assets": HOLIDAYS[state["holiday_key"]]["assets"],
                "return_json": {
                    "title": "short poster title",
                    "subtitle": "short subtitle",
                    "blessing": "one concise blessing sentence",
                    "visual_style": "one of allowed_visual_styles",
                    "selected_assets": "subset of allowed_assets"
                }
            }, ensure_ascii=False)
        }
    ]

    result = call_llm_json(messages, provider_key, model_override, show_debug=True)

    if not result:
        return state

    updated = state.copy()

    updated["title"] = str(result.get("title", state["title"]))[:40]
    updated["subtitle"] = str(result.get("subtitle", state["subtitle"]))[:55]
    updated["blessing"] = str(result.get("blessing", state["blessing"]))[:80]

    if result.get("visual_style") in VISUAL_STYLES:
        updated["visual_style"] = result["visual_style"]

    assets = result.get("selected_assets", state["selected_assets"])
    if isinstance(assets, list):
        allowed = HOLIDAYS[state["holiday_key"]]["assets"]
        filtered = [a for a in assets if a in allowed]
        if filtered:
            updated["selected_assets"] = filtered

    return updated


def revise_state(state, revision_prompt, use_llm, provider_key, model_override):
    if not use_llm:
        return rule_based_revise(state, revision_prompt)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional poster revision assistant. "
                "Return ONLY valid JSON. No markdown. "
                "Use Traditional Chinese. "
                "Only update what the user asks to change."
            )
        },
        {
            "role": "user",
            "content": json.dumps({
                "current_state": state,
                "revision_prompt": revision_prompt,
                "allowed_visual_styles": list(VISUAL_STYLES.keys()),
                "allowed_assets": HOLIDAYS[state["holiday_key"]]["assets"],
                "instruction": "Return complete updated JSON state."
            }, ensure_ascii=False)
        }
    ]

    result = call_llm_json(messages, provider_key, model_override, show_debug=True)

    if not result:
        return rule_based_revise(state, revision_prompt)

    updated = state.copy()

    for key in ["title", "subtitle", "blessing"]:
        if key in result:
            updated[key] = str(result[key])[:90]

    if result.get("visual_style") in VISUAL_STYLES:
        updated["visual_style"] = result["visual_style"]

    if isinstance(result.get("selected_assets"), list):
        allowed = HOLIDAYS[state["holiday_key"]]["assets"]
        filtered = [a for a in result["selected_assets"] if a in allowed]
        if filtered:
            updated["selected_assets"] = filtered

    return updated


def rule_based_revise(state, revision_prompt):
    updated = state.copy()
    text = revision_prompt.lower()

    if "正式" in text or "formal" in text:
        updated["subtitle"] = "廣發證券（香港）謹祝您節日愉快"
        updated["blessing"] = "願您與家人平安順遂，萬事如意。"

    if "高级" in text or "高級" in text:
        updated["visual_style"] = "warm_gold"
        updated["blessing"] = "願佳節暖意常伴，前路豐盈順遂。"

    if "不要快乐" in text or "不要快樂" in text:
        updated["subtitle"] = updated["subtitle"].replace("快樂", "安康").replace("快乐", "安康")
        updated["blessing"] = updated["blessing"].replace("快樂", "安康").replace("快乐", "安康")

    if "红金" in text or "紅金" in text:
        updated["visual_style"] = "red_gold"

    if "水墨" in text:
        updated["visual_style"] = "ink_elegant"

    if "现代" in text or "現代" in text:
        updated["visual_style"] = "modern_brand"

    return updated


# =========================================================
# Renderer
# =========================================================
def render_poster(state, reserve_qr=True):
    width, height = 900, 1600
    bg, text_color, accent = state["colors"]
    style = state["visual_style"]
    assets = state["selected_assets"]

    if style == "red_gold":
        bg = "#B71919"
        text_color = "#FFF4D6"
        accent = "#FFD68A"
    elif style == "modern_brand":
        bg = "#C91616"
        text_color = "#FFF4E0"
        accent = "#FFD68A"
    elif style == "warm_gold":
        bg = "#D99A3D"
        text_color = "#7A4A12"
        accent = "#FFF2C6"
    elif style == "ink_elegant":
        bg = "#F4F0E8"
        text_color = "#222222"
        accent = "#D99A4E"

    img = Image.new("RGB", (width, height), bg)
    img = add_noise(img, opacity=8)
    draw = ImageDraw.Draw(img)

    if "moon" in assets:
        draw_moon_scene(draw, width, height)

    if "mountain" in assets:
        draw_mountain_scene(draw, width, height)

    if "lantern" in assets:
        draw_lantern(draw, 35, 80, 1.0)
        draw_lantern(draw, width - 105, 80, 1.0)

    if "firework" in assets:
        draw_firework(draw, 210, 360, 75, accent)
        draw_firework(draw, 710, 430, 85, accent)

    if "red_packet" in assets:
        draw_red_packet(draw, width, height)

    if "christmas_tree" in assets:
        draw_christmas_tree(draw, width // 2, 620)

    if "city" in assets or "city_silhouette" in assets:
        draw_city(draw, width, height)

    if "wave" in assets:
        draw_wave(draw, width, height)

    if "lotus" in assets:
        draw_lotus(draw, width, height)

    if style == "modern_brand" and "moon" not in assets:
        draw_modern_geometry(draw, width, height)

    brand_color = "#E4D0A1" if bg.lower() not in ["#f4f0e8", "#f3efe2"] else "#B8A06A"
    draw_brand(draw, 70, 70, color=brand_color, scale=0.7)

    title_font = load_font(86, bold=True)
    title_font_small = load_font(74, bold=True)
    subtitle_font = load_font(36, bold=False)
    body_font = load_font(32, bold=False)

    y = 260
    for line in state["title"].split("\n"):
        font = title_font if len(line) <= 6 else title_font_small
        centered_text(draw, line, y, font, text_color, width)
        y += font.size + 18

    centered_text(draw, state["subtitle"], y + 35, subtitle_font, text_color, width)
    centered_text(draw, state["blessing"], y + 95, body_font, text_color, width)

    draw.pieslice([-160, height - 350, width + 160, height + 220], 180, 360, fill="#FFFFFF")
    draw_brand(draw, 70, height - 150, color="#B8A06A", scale=0.75)

    if reserve_qr:
        draw_qr_placeholder(draw, width, height)

    return img


# =========================================================
# UI
# =========================================================
st.title("🎨 GF Securities Festival Poster Agent")
st.write("Generate company-style festival greeting posters with optional LLM copywriting.")

with st.sidebar:
    st.header("Poster Settings")

    holiday_key = st.selectbox(
        "节日主题 / Holiday Theme",
        options=list(HOLIDAYS.keys()),
        index=list(HOLIDAYS.keys()).index("mid_autumn"),
        format_func=lambda x: HOLIDAYS[x]["name"],
    )

    visual_style = st.selectbox(
        "视觉风格 / Visual Style",
        options=list(VISUAL_STYLES.keys()),
        format_func=lambda x: VISUAL_STYLES[x],
    )

    reserve_qr = st.checkbox("Reserve QR area / 预留二维码位置", value=True)

    st.divider()

    st.header("AI Provider")

    use_llm = st.toggle("Use LLM for copywriting", value=True)

    provider_options = ["auto"] + list(PROVIDERS.keys())
    provider_key = st.selectbox(
        "Provider",
        options=provider_options,
        format_func=lambda x: "Auto / 自动选择可用 Provider" if x == "auto" else PROVIDERS[x]["label"],
    )

    default_model = ""
    if provider_key != "auto":
        default_model = get_provider_config(provider_key)["model"]

    model_override = st.text_input(
        "Model",
        value=default_model,
        placeholder="Leave empty to use model from Secrets",
    )

    if use_llm:
        available = get_available_providers()
        if provider_key == "auto":
            if available:
                st.success("Configured: " + ", ".join([PROVIDERS[x]["label"] for x in available]))
            else:
                st.warning("No provider configured in Secrets.")
        else:
            cfg = get_provider_config(provider_key, model_override)
            if cfg["api_key"] and cfg["base_url"] and cfg["model"]:
                st.success(f"{cfg['label']} configured")
            else:
                st.warning("Selected provider is not fully configured.")

    st.divider()

    if st.button("Test LLM Connection"):
        test_messages = [
            {"role": "system", "content": "Return ONLY valid JSON. No markdown."},
            {"role": "user", "content": "{\"status\":\"ok\"}"},
        ]

        result = call_llm_json(
            messages=test_messages,
            provider_key=provider_key,
            model_override=model_override,
            show_debug=True,
        )

        if result:
            st.success(f"Test succeeded: {result}")
        else:
            st.error("Test failed. Check the error message above.")


st.divider()

st.subheader("1. Generate Poster")

prompt = st.text_area(
    "输入文案要求 / Copywriting instruction",
    value="面向客户，语气正式温暖，文案不要太俗套，保留节日氛围。",
    height=120,
)

if st.button("Generate Poster"):
    if not prompt.strip():
        st.warning("Please enter a copywriting instruction.")
    else:
        with st.spinner("Generating poster..."):
            state = generate_base_state(holiday_key, visual_style)

            if use_llm:
                state = generate_state_with_llm(
                    state=state,
                    user_prompt=prompt,
                    provider_key=provider_key,
                    model_override=model_override,
                )

            poster = render_poster(state, reserve_qr=reserve_qr)

            st.session_state["poster_state"] = state
            st.session_state["poster"] = poster

        st.success("Poster generated.")

        col1, col2 = st.columns([1.25, 1])

        with col1:
            st.image(poster, caption="Generated Poster Preview", use_container_width=False)

            st.download_button(
                "Download Poster as PNG",
                data=image_to_bytes(poster),
                file_name="gf_festival_poster.png",
                mime="image/png",
            )

        with col2:
            st.subheader("Generation Summary")
            st.write(f"**Holiday:** {state['holiday_name']}")
            st.write(f"**Visual style:** {VISUAL_STYLES.get(state['visual_style'], state['visual_style'])}")
            st.write(f"**Selected assets:** {', '.join(state['selected_assets'])}")

            with st.expander("Debug JSON"):
                st.json(state)


st.divider()

st.subheader("2. Revise Poster")

revision_prompt = st.text_area(
    "输入修改指令 / Revision instruction",
    placeholder="例如：文案更正式一点 / 不要出现快乐 / 保留风格，只改祝福语 / 改成更高级的语气",
    height=100,
)

if st.button("Apply Revision"):
    if "poster_state" not in st.session_state:
        st.warning("Please generate a poster first.")
    elif not revision_prompt.strip():
        st.warning("Please enter a revision instruction.")
    else:
        with st.spinner("Applying revision..."):
            updated_state = revise_state(
                state=st.session_state["poster_state"],
                revision_prompt=revision_prompt,
                use_llm=use_llm,
                provider_key=provider_key,
                model_override=model_override,
            )

            poster = render_poster(updated_state, reserve_qr=reserve_qr)

            st.session_state["poster_state"] = updated_state
            st.session_state["poster"] = poster

        st.success("Revision applied.")

        col1, col2 = st.columns([1.25, 1])

        with col1:
            st.image(poster, caption="Revised Poster Preview", use_container_width=False)

            st.download_button(
                "Download Revised Poster as PNG",
                data=image_to_bytes(poster),
                file_name="gf_festival_poster_revised.png",
                mime="image/png",
            )

        with col2:
            st.subheader("Revision Summary")
            st.write(f"**Holiday:** {updated_state['holiday_name']}")
            st.write(f"**Visual style:** {VISUAL_STYLES.get(updated_state['visual_style'], updated_state['visual_style'])}")
            st.write(f"**Selected assets:** {', '.join(updated_state['selected_assets'])}")

            with st.expander("Debug JSON"):
                st.json(updated_state)

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import json
import re
import math

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
# Holiday data
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
        "tone": "modern, festive, hopeful",
        "default_main_visual": "firework",
    },
    "spring_festival": {
        "name": "春节 / Chinese New Year",
        "title": "恭賀新春",
        "subtitle": "廣發證券（香港）祝您新春快樂",
        "blessing": "馬到功成，財源廣進。",
        "colors": ["#B71919", "#FFF4D6", "#FFD68A"],
        "assets": ["lantern", "firework", "red_packet", "gold_cloud"],
        "style": "red_gold",
        "tone": "festive, warm, prosperous, corporate",
        "default_main_visual": "red_packet",
    },
    "qingming": {
        "name": "清明节 / Ching Ming Festival",
        "title": "清明安康",
        "subtitle": "慎終追遠，春和景明",
        "blessing": "願您與家人平安順遂，萬事安康。",
        "colors": ["#F4F0E8", "#222222", "#D99A4E"],
        "assets": ["mountain", "sun", "branch", "bird"],
        "style": "ink_elegant",
        "tone": "calm, elegant, restrained",
        "default_main_visual": "mountain",
    },
    "easter": {
        "name": "复活节 / Easter",
        "title": "Happy Easter",
        "subtitle": "復活節快樂",
        "blessing": "願春日暖意與美好祝福常伴您左右。",
        "colors": ["#F7F3E8", "#333333", "#D8A15D"],
        "assets": ["soft_light", "circle"],
        "style": "ink_elegant",
        "tone": "soft, clear, professional",
        "default_main_visual": "soft_light",
    },
    "labour_day": {
        "name": "劳动节 / Labour Day",
        "title": "勞動節快樂",
        "subtitle": "致敬每一份努力與堅持",
        "blessing": "廣發證券（香港）祝您假期愉快，身心舒暢。",
        "colors": ["#C91616", "#FFF4D6", "#FFD68A"],
        "assets": ["firework", "gold_curve", "brand_symbol"],
        "style": "modern_brand",
        "tone": "energetic, positive, corporate",
        "default_main_visual": "firework",
    },
    "buddha_birthday": {
        "name": "佛诞 / Buddha's Birthday",
        "title": "佛誕吉祥",
        "subtitle": "廣發證券（香港）祝您佛誕安康",
        "blessing": "願心境澄明，福慧常伴，萬事順遂。",
        "colors": ["#F3EFE2", "#222222", "#D8A15D"],
        "assets": ["sun", "cloud", "lotus"],
        "style": "ink_elegant",
        "tone": "peaceful, elegant, formal",
        "default_main_visual": "lotus",
    },
    "dragon_boat": {
        "name": "端午节 / Dragon Boat Festival",
        "title": "端午安康",
        "subtitle": "粽香盈袖，福至安康",
        "blessing": "廣發證券（香港）祝您端午安康。",
        "colors": ["#0F766E", "#FFF8E7", "#F2C16B"],
        "assets": ["wave", "boat", "gold_curve"],
        "style": "warm_gold",
        "tone": "traditional, energetic, festive",
        "default_main_visual": "boat",
    },
    "hk_sar_day": {
        "name": "香港特别行政区成立纪念日 / HKSAR Establishment Day",
        "title": "九州同慶\n盛世華誕",
        "subtitle": "香港特別行政區成立紀念日",
        "blessing": "同心同行，共啟新程。",
        "colors": ["#B71919", "#FFF4D6", "#FFD68A"],
        "assets": ["city", "firework", "brand_symbol"],
        "style": "red_gold",
        "tone": "formal, celebratory, civic",
        "default_main_visual": "city",
    },
    "mid_autumn": {
        "name": "中秋节 / Mid-Autumn Festival",
        "title": "情滿中秋\n月圓人團圓",
        "subtitle": "廣發證券（香港）祝您中秋快樂",
        "blessing": "月滿人團圓，佳節共安康。",
        "colors": ["#D99A3D", "#7A4A12", "#FFF2C6"],
        "assets": ["moon", "rabbit", "cloud", "branch", "water_reflection"],
        "style": "warm_gold",
        "tone": "warm, elegant, poetic, client-facing",
        "default_main_visual": "moon",
    },
    "national_day": {
        "name": "国庆日 / National Day",
        "title": "國慶快樂",
        "subtitle": "山河錦繡，盛世同慶",
        "blessing": "廣發證券（香港）祝您假期愉快。",
        "colors": ["#B71919", "#FFF4D6", "#FFD68A"],
        "assets": ["firework", "city", "gold_curve"],
        "style": "red_gold",
        "tone": "grand, festive, formal",
        "default_main_visual": "city",
    },
    "chung_yeung": {
        "name": "重阳节 / Chung Yeung Festival",
        "title": "重陽安康",
        "subtitle": "登高望遠，秋意綿長",
        "blessing": "廣發證券（香港）祝您重陽安康，順遂如意。",
        "colors": ["#F4F0E8", "#222222", "#D99A4E"],
        "assets": ["mountain", "sun", "branch", "bird"],
        "style": "ink_elegant",
        "tone": "traditional, calm, elegant",
        "default_main_visual": "mountain",
    },
    "thanksgiving": {
        "name": "感恩节 / Thanksgiving",
        "title": "Thanksgiving",
        "subtitle": "感恩相伴",
        "blessing": "感謝一路同行，願溫暖與收穫常伴左右。",
        "colors": ["#F5D06F", "#7A4A12", "#D99A3D"],
        "assets": ["warm_light", "gold_gradient"],
        "style": "warm_gold",
        "tone": "warm, grateful, client-facing",
        "default_main_visual": "warm_light",
    },
    "christmas": {
        "name": "圣诞节 / Christmas",
        "title": "MERRY\nCHRISTMAS",
        "subtitle": "聖誕快樂",
        "blessing": "願節日的溫暖與喜悅常伴您左右。",
        "colors": ["#C91616", "#FFF4D6", "#0C6B4E"],
        "assets": ["christmas_tree", "snowflake", "star", "gift"],
        "style": "modern_brand",
        "tone": "festive, joyful, warm",
        "default_main_visual": "christmas_tree",
    },
}


VISUAL_STYLES = {
    "auto": "Auto based on holiday / 根据节日自动匹配",
    "red_gold": "红金节庆",
    "warm_gold": "暖金高级",
    "ink_elegant": "水墨雅致",
    "modern_brand": "现代品牌红",
}

LAYOUT_OPTIONS = {
    "auto": "Auto / 自动",
    "top_text": "Top text / 文案上方",
    "center_text": "Center text / 文案居中",
    "bottom_text": "Bottom text / 文案下方",
}

DENSITY_OPTIONS = {
    "low": "Low / 简洁",
    "medium": "Medium / 适中",
    "high": "High / 丰富",
}


# OpenRouter 默认不再使用 qwen/qwen3-coder:free
PROVIDERS = {
    "openrouter": {
        "label": "OpenRouter",
        "api_key_secret": "OPENROUTER_API_KEY",
        "base_url_secret": "OPENROUTER_BASE_URL",
        "default_base_url": "https://openrouter.ai/api/v1",
        "default_model": "openrouter/free",
    },
    "groq": {
        "label": "Groq",
        "api_key_secret": "GROQ_API_KEY",
        "base_url_secret": "GROQ_BASE_URL",
        "default_base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-8b-instant",
    },
    "siliconflow": {
        "label": "SiliconFlow 硅基流动",
        "api_key_secret": "SILICONFLOW_API_KEY",
        "base_url_secret": "SILICONFLOW_BASE_URL",
        "default_base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
    },
    "custom": {
        "label": "Custom OpenAI-compatible API",
        "api_key_secret": "CUSTOM_API_KEY",
        "base_url_secret": "CUSTOM_BASE_URL",
        "default_base_url": "",
        "default_model": "",
    },
}

MODEL_PRESETS = {
    "openrouter": ["openrouter/free", "custom model..."],
    "groq": ["llama-3.1-8b-instant", "custom model..."],
    "siliconflow": ["Qwen/Qwen2.5-7B-Instruct", "custom model..."],
    "custom": ["custom model..."],
}


# =========================================================
# Secrets / provider helpers
# =========================================================
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def mask_key(key):
    if not key:
        return "Not found"
    if len(key) < 12:
        return "***"
    return key[:5] + "..." + key[-4:]


def get_provider_config(provider_key, selected_model):
    provider = PROVIDERS[provider_key]

    api_key = get_secret(provider["api_key_secret"], "")
    base_url = get_secret(provider["base_url_secret"], provider["default_base_url"])

    model = selected_model.strip()
    if not model or model == "custom model...":
        model = provider["default_model"]

    return {
        "key": provider_key,
        "label": provider["label"],
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def call_llm_text(messages, provider_key, selected_model, show_debug=True):
    if OpenAI is None:
        st.error("openai package is not installed. Please add `openai` to requirements.txt.")
        return None

    cfg = get_provider_config(provider_key, selected_model)

    if not cfg["api_key"] or not cfg["base_url"] or not cfg["model"]:
        st.error(
            f"{cfg['label']} is not fully configured.\n\n"
            f"API key: {mask_key(cfg['api_key'])}\n\n"
            f"Base URL: {cfg['base_url']}\n\n"
            f"Model: {cfg['model']}"
        )
        return None

    try:
        client = OpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
        )

        kwargs = {
            "model": cfg["model"],
            "messages": messages,
            "temperature": 0.25,
            "max_tokens": 1000,
        }

        if provider_key == "openrouter":
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
        content = response.choices[0].message.content or ""

        if show_debug:
            st.success(f"LLM call succeeded: {cfg['label']}")
            with st.expander("Raw model response"):
                st.code(content[:3000])

        return content.strip()

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
# Model output parser
# =========================================================
def parse_model_output(text, base_state):
    updated = base_state.copy()

    if not text:
        return updated

    data = None

    try:
        data = json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except Exception:
                data = None

    if isinstance(data, dict):
        if data.get("title"):
            updated["title"] = str(data["title"])[:45]

        if data.get("subtitle"):
            updated["subtitle"] = str(data["subtitle"])[:65]

        if data.get("blessing"):
            updated["blessing"] = str(data["blessing"])[:95]

        if data.get("visual_style") in ["red_gold", "warm_gold", "ink_elegant", "modern_brand"]:
            updated["visual_style"] = data["visual_style"]

        if data.get("layout_mode") in ["top_text", "center_text", "bottom_text"]:
            updated["layout_mode"] = data["layout_mode"]

        if data.get("main_visual") in HOLIDAYS[updated["holiday_key"]]["assets"]:
            updated["main_visual"] = data["main_visual"]

        if data.get("main_visual_position") in ["upper", "middle", "lower"]:
            updated["main_visual_position"] = data["main_visual_position"]

        if data.get("element_density") in ["low", "medium", "high"]:
            updated["element_density"] = data["element_density"]

        if isinstance(data.get("main_visual_scale"), (int, float)):
            updated["main_visual_scale"] = max(0.7, min(1.45, float(data["main_visual_scale"])))

        if isinstance(data.get("selected_assets"), list):
            allowed = HOLIDAYS[updated["holiday_key"]]["assets"]
            filtered = [a for a in data["selected_assets"] if a in allowed]
            if filtered:
                updated["selected_assets"] = filtered

        if updated.get("main_visual") not in updated.get("selected_assets", []):
            allowed = HOLIDAYS[updated["holiday_key"]]["assets"]
            if updated.get("main_visual") in allowed:
                updated["selected_assets"] = [updated["main_visual"]] + updated.get("selected_assets", [])

        return updated

    patterns = {
        "title": r"(?:title|TITLE|Title|標題|标题)\s*[:：]\s*(.+)",
        "subtitle": r"(?:subtitle|SUBTITLE|Subtitle|副標題|副标题)\s*[:：]\s*(.+)",
        "blessing": r"(?:blessing|BLESSING|Blessing|祝福語|祝福语|文案)\s*[:：]\s*(.+)",
    }

    changed = False

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            updated[key] = match.group(1).strip().strip('"').strip("'")[:95]
            changed = True

    if not changed:
        clean = re.sub(r"\s+", " ", text).strip()
        if clean:
            updated["blessing"] = clean[:95]

    return updated


# =========================================================
# Rule layer for visible layout changes
# =========================================================
def apply_prompt_rules(state, prompt):
    updated = state.copy()
    lower_text = prompt.lower()

    if any(k in prompt for k in ["中間", "中间", "居中", "中央", "图片中间", "圖片中間", "画面中间", "畫面中間"]):
        updated["layout_mode"] = "center_text"
        updated["main_visual_position"] = "middle"

    if any(k in prompt for k in ["顶部", "頂部", "上方", "上面"]):
        updated["layout_mode"] = "top_text"
        updated["main_visual_position"] = "middle"

    if any(k in prompt for k in ["底部", "下方", "下面"]):
        updated["layout_mode"] = "bottom_text"
        updated["main_visual_position"] = "upper"

    if any(k in prompt for k in ["多一些", "多点", "多一點", "丰富", "豐富", "元素多"]):
        updated["element_density"] = "high"
        allowed = HOLIDAYS[updated["holiday_key"]]["assets"]
        updated["selected_assets"] = allowed

    if any(k in prompt for k in ["少一点", "少一點", "简洁", "簡潔", "干净", "乾淨"]):
        updated["element_density"] = "low"
        updated["selected_assets"] = updated["selected_assets"][:2]

    if any(k in prompt for k in ["月亮大", "大月亮", "主视觉大", "主視覺大"]):
        updated["main_visual_scale"] = 1.25

    if any(k in prompt for k in ["月亮小", "主视觉小", "主視覺小"]):
        updated["main_visual_scale"] = 0.85

    if "红金" in prompt or "紅金" in prompt:
        updated["visual_style"] = "red_gold"

    if "暖金" in prompt or "高级" in prompt or "高級" in prompt:
        updated["visual_style"] = "warm_gold"

    if "水墨" in prompt or "雅致" in prompt:
        updated["visual_style"] = "ink_elegant"

    if "现代" in prompt or "現代" in prompt or "品牌" in prompt:
        updated["visual_style"] = "modern_brand"

    if "red" in lower_text and "gold" in lower_text:
        updated["visual_style"] = "red_gold"

    if "center" in lower_text or "middle" in lower_text:
        updated["layout_mode"] = "center_text"

    if "more elements" in lower_text or "rich" in lower_text:
        updated["element_density"] = "high"

    return updated


# =========================================================
# Font helpers
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


def add_subtle_texture(img, opacity=5):
    overlay = Image.new("RGB", img.size, "#FFFFFF")
    return Image.blend(img, overlay, opacity / 255)


def add_text_panel(img, x1, y1, x2, y2, color="#000000", opacity=45):
    rgba = img.convert("RGBA")
    overlay = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    d.rounded_rectangle([x1, y1, x2, y2], radius=28, fill=rgb + (opacity,))

    return Image.alpha_composite(rgba, overlay).convert("RGB")


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
        width=max(2, int(5 * scale)),
    )

    draw.text((x + int(85 * scale), y), "廣發證券（香港）", font=name_font, fill=color)
    draw.text(
        (x + int(87 * scale), y + int(50 * scale)),
        "GF SECURITIES (HONG KONG)",
        font=en_font,
        fill=color,
    )


def draw_firework(draw, cx, cy, r, color="#FFD68A", width=3):
    for i in range(20):
        angle = 2 * math.pi * i / 20
        x1 = cx + math.cos(angle) * r * 0.25
        y1 = cy + math.sin(angle) * r * 0.25
        x2 = cx + math.cos(angle) * r
        y2 = cy + math.sin(angle) * r
        draw.line([x1, y1, x2, y2], fill=color, width=width)


def draw_lantern(draw, x, y, scale=1.0):
    w = int(70 * scale)
    h = int(110 * scale)

    draw.line([x + w // 2, y - 35, x + w // 2, y], fill="#FFD68A", width=3)
    draw.ellipse([x, y, x + w, y + h], fill="#D7261E", outline="#FFD68A", width=3)
    draw.rectangle([x + 20, y + h - 5, x + w - 20, y + h + 10], fill="#FFD68A")
    draw.line([x + w // 2, y + h + 10, x + w // 2, y + h + 45], fill="#FFD68A", width=2)


def draw_moon_scene(draw, width, height, cx=450, cy=720, scale=1.0, density="medium"):
    r = int(245 * scale)

    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FFF4C8")
    draw.ellipse(
        [
            cx - int(r * 0.73),
            cy - int(r * 0.73),
            cx + int(r * 0.73),
            cy + int(r * 0.73),
        ],
        fill="#FBE7A5",
    )

    cloud_y = cy + int(20 * scale)
    draw.ellipse([cx + 25, cloud_y - 50, cx + 200, cloud_y + 25], fill="#FFF9D8")
    draw.ellipse([cx + 130, cloud_y - 80, cx + 300, cloud_y + 20], fill="#FFF9D8")
    draw.rectangle([cx + 25, cloud_y - 15, cx + 300, cloud_y + 25], fill="#FFF9D8")

    rabbit_x = cx - int(40 * scale)
    rabbit_y = cy + int(165 * scale)
    draw.ellipse([rabbit_x - 65, rabbit_y - 55, rabbit_x + 75, rabbit_y + 90], fill="#DFAE45")
    draw.ellipse([rabbit_x - 28, rabbit_y - 112, rabbit_x + 12, rabbit_y - 20], fill="#DFAE45")
    draw.ellipse([rabbit_x + 25, rabbit_y - 112, rabbit_x + 65, rabbit_y - 20], fill="#DFAE45")

    if density in ["medium", "high"]:
        for i in range(5):
            draw.line(
                [60, 430 + i * 30, 300, 335 + i * 18],
                fill="#8A5A20",
                width=4,
            )

    if density == "high":
        for i in range(6):
            draw_firework(draw, 140 + i * 120, 1030 + (i % 2) * 50, 28, "#FFE8A8", width=2)

        for i in range(7):
            y = 930 + i * 22
            draw.arc([250 - i * 18, y, 640 + i * 18, y + 60], 10, 170, fill="#F7D879", width=3)


def draw_mountain_scene(draw, width, height, density="medium"):
    draw.ellipse([610, 220, 790, 400], fill="#E7A15F")
    draw.polygon([(0, 430), (130, 330), (250, 440)], fill="#D8D8D8")
    draw.polygon([(620, 520), (760, 410), (930, 520)], fill="#D0D0D0")
    draw.polygon([(360, 500), (520, 410), (690, 510)], fill="#E1E1E1")

    if density in ["medium", "high"]:
        for i in range(6):
            x = 40 + i * 20
            draw.arc([x, 520 - i * 8, x + 180, 760], 210, 285, fill="#C8B27D", width=2)


def draw_christmas_tree(draw, cx, cy, scale=1.0):
    draw_firework(draw, cx, cy - 30, int(35 * scale), "#FFD68A")

    draw.polygon(
        [
            (cx, cy),
            (cx - int(170 * scale), cy + int(260 * scale)),
            (cx + int(170 * scale), cy + int(260 * scale)),
        ],
        fill="#0C6B4E",
    )
    draw.polygon(
        [
            (cx, cy + int(160 * scale)),
            (cx - int(215 * scale), cy + int(460 * scale)),
            (cx + int(215 * scale), cy + int(460 * scale)),
        ],
        fill="#0C6B4E",
    )
    draw.rectangle(
        [
            cx - int(36 * scale),
            cy + int(460 * scale),
            cx + int(36 * scale),
            cy + int(575 * scale),
        ],
        fill="#0C6B4E",
    )


def draw_red_packet(draw, width, height, cx=450, cy=700, scale=1.0):
    w = int(380 * scale)
    h = int(330 * scale)
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], radius=32, fill="#FCE6B0")
    draw.rounded_rectangle(
        [cx - w // 2 + 45, cy - h // 2 + 50, cx + w // 2 - 45, cy + h // 2 - 40],
        radius=22,
        fill="#D92020",
    )
    draw.ellipse([cx - 70, cy - 60, cx + 70, cy + 80], fill="#F7B15A")


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


def draw_lotus(draw, width, height, cx=450, cy=760, scale=1.0):
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + int(math.cos(angle) * 90 * scale)
        y = cy + int(math.sin(angle) * 45 * scale)
        draw.ellipse([x - 70, y - 35, x + 70, y + 35], fill="#E2B46A")
    draw.ellipse([cx - 90, cy - 45, cx + 90, cy + 45], fill="#F7E7A8")


def draw_qr_placeholder(draw, width, height):
    draw.rounded_rectangle(
        [700, height - 170, 820, height - 50],
        radius=12,
        outline="#D8D8D8",
        width=3,
    )
    draw.text((705, height - 25), "QR reserved", fill="#999999", font=load_font(18))


# =========================================================
# Poster state
# =========================================================
def resolve_style(holiday_key, visual_style):
    if visual_style != "auto":
        return visual_style
    return HOLIDAYS.get(holiday_key, HOLIDAYS["mid_autumn"]).get("style", "warm_gold")


def generate_base_state(holiday_key, visual_style, layout_mode, element_density):
    holiday = HOLIDAYS.get(holiday_key, HOLIDAYS["mid_autumn"])

    resolved_layout = layout_mode
    if resolved_layout == "auto":
        resolved_layout = "top_text"

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
        "layout_mode": resolved_layout,
        "main_visual": holiday.get("default_main_visual", "moon"),
        "main_visual_position": "middle",
        "main_visual_scale": 1.0,
        "element_density": element_density,
    }


def generate_state_with_llm(state, user_prompt, provider_key, selected_model, show_debug):
    allowed_assets = HOLIDAYS[state["holiday_key"]]["assets"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional corporate poster art director and copywriter. "
                "Use Traditional Chinese. Keep text concise. "
                "You must control both text and visual layout. No markdown. Return JSON if possible."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Holiday: {state['holiday_name']}\n"
                f"Current title: {state['title']}\n"
                f"Current subtitle: {state['subtitle']}\n"
                f"Current blessing: {state['blessing']}\n"
                f"Allowed visual styles: red_gold, warm_gold, ink_elegant, modern_brand\n"
                f"Allowed layout_mode: top_text, center_text, bottom_text\n"
                f"Allowed main_visual_position: upper, middle, lower\n"
                f"Allowed element_density: low, medium, high\n"
                f"Allowed assets: {', '.join(allowed_assets)}\n"
                f"User instruction: {user_prompt}\n\n"
                "Return JSON with these keys:\n"
                "{\n"
                '  "title": "...",\n'
                '  "subtitle": "...",\n'
                '  "blessing": "...",\n'
                '  "visual_style": "warm_gold",\n'
                '  "layout_mode": "center_text",\n'
                '  "main_visual": "moon",\n'
                '  "main_visual_position": "middle",\n'
                '  "main_visual_scale": 1.15,\n'
                '  "element_density": "high",\n'
                '  "selected_assets": ["moon", "rabbit", "cloud", "branch"]\n'
                "}"
            ),
        },
    ]

    text = call_llm_text(messages, provider_key, selected_model, show_debug=show_debug)
    state = parse_model_output(text, state)
    state = apply_prompt_rules(state, user_prompt)
    return state


def rule_based_revise(state, revision_prompt):
    updated = apply_prompt_rules(state, revision_prompt)
    text = revision_prompt.lower()

    if "正式" in text or "formal" in text:
        updated["subtitle"] = "廣發證券（香港）謹祝您節日愉快"
        updated["blessing"] = "願您與家人平安順遂，萬事如意。"

    if "不要快乐" in text or "不要快樂" in text:
        updated["subtitle"] = updated["subtitle"].replace("快樂", "安康").replace("快乐", "安康")
        updated["blessing"] = updated["blessing"].replace("快樂", "安康").replace("快乐", "安康")

    return updated


def revise_state(state, revision_prompt, use_llm, provider_key, selected_model, show_debug):
    if not use_llm:
        return rule_based_revise(state, revision_prompt)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional poster revision assistant. "
                "Use Traditional Chinese. Keep text concise. "
                "Update text, layout, and visual controls according to the instruction. No markdown. Return JSON if possible."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Current poster state:\n{json.dumps(state, ensure_ascii=False)}\n\n"
                f"Revision instruction: {revision_prompt}\n\n"
                "Return updated JSON with keys: title, subtitle, blessing, visual_style, layout_mode, "
                "main_visual, main_visual_position, main_visual_scale, element_density, selected_assets."
            ),
        },
    ]

    text = call_llm_text(messages, provider_key, selected_model, show_debug=show_debug)
    updated = parse_model_output(text, state)
    updated = apply_prompt_rules(updated, revision_prompt)

    if updated == state:
        return rule_based_revise(state, revision_prompt)

    return updated


# =========================================================
# Renderer
# =========================================================
def get_visual_center(state):
    pos = state.get("main_visual_position", "middle")

    if pos == "upper":
        return 450, 500
    if pos == "lower":
        return 450, 920
    return 450, 720


def get_text_y(state):
    layout = state.get("layout_mode", "top_text")

    if layout == "center_text":
        return 540
    if layout == "bottom_text":
        return 900
    return 260


def render_poster(state, reserve_qr=True):
    width, height = 900, 1600
    bg, text_color, accent = state["colors"]
    style = state["visual_style"]
    assets = state["selected_assets"]
    density = state.get("element_density", "medium")
    scale = float(state.get("main_visual_scale", 1.0))
    cx, cy = get_visual_center(state)

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
    img = add_subtle_texture(img, opacity=8)
    draw = ImageDraw.Draw(img)

    if style == "modern_brand" and "moon" not in assets:
        draw_modern_geometry(draw, width, height)

    if "mountain" in assets:
        draw_mountain_scene(draw, width, height, density=density)

    if "moon" in assets:
        draw_moon_scene(draw, width, height, cx=cx, cy=cy, scale=scale, density=density)

    if "lantern" in assets:
        draw_lantern(draw, 35, 80, 1.0)
        draw_lantern(draw, width - 105, 80, 1.0)

    if "firework" in assets:
        draw_firework(draw, 210, 360, 75, accent)
        draw_firework(draw, 710, 430, 85, accent)
        if density == "high":
            draw_firework(draw, 130, 1120, 50, accent)
            draw_firework(draw, 760, 980, 45, accent)

    if "red_packet" in assets:
        draw_red_packet(draw, width, height, cx=cx, cy=cy, scale=scale)

    if "christmas_tree" in assets:
        draw_christmas_tree(draw, width // 2, 560, scale=scale)

    if "city" in assets:
        draw_city(draw, width, height)

    if "wave" in assets:
        draw_wave(draw, width, height)

    if "lotus" in assets:
        draw_lotus(draw, width, height, cx=cx, cy=cy, scale=scale)

    brand_color = "#E4D0A1" if bg.lower() not in ["#f4f0e8", "#f3efe2"] else "#B8A06A"
    draw_brand(draw, 70, 70, color=brand_color, scale=0.7)

    layout = state.get("layout_mode", "top_text")
    if layout == "center_text":
        panel_color = "#000000" if style in ["red_gold", "modern_brand"] else "#FFFFFF"
        img = add_text_panel(img, 95, 500, 805, 760, color=panel_color, opacity=58)
        draw = ImageDraw.Draw(img)
    elif layout == "bottom_text":
        panel_color = "#000000" if style in ["red_gold", "modern_brand"] else "#FFFFFF"
        img = add_text_panel(img, 95, 865, 805, 1090, color=panel_color, opacity=48)
        draw = ImageDraw.Draw(img)

    title_font = load_font(82, bold=True)
    title_font_small = load_font(68, bold=True)
    subtitle_font = load_font(34, bold=False)
    body_font = load_font(30, bold=False)

    y = get_text_y(state)

    for line in state["title"].split("\n"):
        font = title_font if len(line) <= 7 else title_font_small
        centered_text(draw, line, y, font, text_color, width)
        y += font.size + 14

    centered_text(draw, state["subtitle"], y + 28, subtitle_font, text_color, width)
    centered_text(draw, state["blessing"], y + 82, body_font, text_color, width)

    draw.pieslice([-160, height - 350, width + 160, height + 220], 180, 360, fill="#FFFFFF")
    draw_brand(draw, 70, height - 150, color="#B8A06A", scale=0.75)

    if reserve_qr:
        draw_qr_placeholder(draw, width, height)

    return img


# =========================================================
# UI
# =========================================================
st.title("🎨 GF Securities Festival Poster Agent")
st.write("Generate company-style festival greeting posters with LLM-controlled copywriting and layout.")

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

    layout_mode = st.selectbox(
        "版式 / Layout",
        options=list(LAYOUT_OPTIONS.keys()),
        index=0,
        format_func=lambda x: LAYOUT_OPTIONS[x],
    )

    element_density = st.selectbox(
        "元素密度 / Element density",
        options=list(DENSITY_OPTIONS.keys()),
        index=1,
        format_func=lambda x: DENSITY_OPTIONS[x],
    )

    reserve_qr = st.checkbox("Reserve QR area / 预留二维码位置", value=True)

    st.divider()
    st.header("AI Provider")

    use_llm = st.toggle("Use LLM for copywriting & layout", value=True)

    provider_key = st.selectbox(
        "Provider",
        options=list(PROVIDERS.keys()),
        index=0,
        format_func=lambda x: PROVIDERS[x]["label"],
    )

    model_presets = MODEL_PRESETS.get(provider_key, ["custom model..."])
    model_choice = st.selectbox("Model preset", options=model_presets, index=0)

    if model_choice == "custom model...":
        selected_model = st.text_input("Custom model", value="", placeholder="Example: openrouter/free")
    else:
        selected_model = model_choice

    show_debug = st.checkbox("Show LLM debug", value=True)

    cfg = get_provider_config(provider_key, selected_model)

    if use_llm:
        if cfg["api_key"] and cfg["base_url"] and cfg["model"]:
            st.success(f"Configured: {cfg['label']} / {cfg['model']}")
        else:
            st.warning("Selected provider is not fully configured.")

    st.divider()

    if st.button("Test LLM Connection"):
        test_messages = [
            {"role": "system", "content": "Reply with one short sentence."},
            {"role": "user", "content": "Say: API connection works."},
        ]

        result = call_llm_text(test_messages, provider_key, selected_model, show_debug=True)

        if result:
            st.success("Raw LLM response:")
            st.write(result)
        else:
            st.error("Test failed. Check the error message above.")


st.divider()
st.subheader("1. Generate Poster")

prompt = st.text_area(
    "输入文案和版式要求 / Copywriting & layout instruction",
    value="面向客户，语气正式温暖，文案不要太俗套，保留节日氛围。文案放在图片中间，画面多一些节日元素。",
    height=130,
)

if st.button("Generate Poster"):
    if not prompt.strip():
        st.warning("Please enter a copywriting instruction.")
    else:
        with st.spinner("Generating poster..."):
            state = generate_base_state(
                holiday_key=holiday_key,
                visual_style=visual_style,
                layout_mode=layout_mode,
                element_density=element_density,
            )

            if use_llm:
                state = generate_state_with_llm(
                    state=state,
                    user_prompt=prompt,
                    provider_key=provider_key,
                    selected_model=selected_model,
                    show_debug=show_debug,
                )
            else:
                state = apply_prompt_rules(state, prompt)

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
            st.write(f"**Layout:** {LAYOUT_OPTIONS.get(state['layout_mode'], state['layout_mode'])}")
            st.write(f"**Density:** {DENSITY_OPTIONS.get(state['element_density'], state['element_density'])}")
            st.write(f"**Main visual:** {state['main_visual']} / {state['main_visual_position']} / scale {state['main_visual_scale']}")
            st.write(f"**Selected assets:** {', '.join(state['selected_assets'])}")

            with st.expander("Debug JSON"):
                st.json(state)


st.divider()
st.subheader("2. Revise Poster")

revision_prompt = st.text_area(
    "输入修改指令 / Revision instruction",
    placeholder="例如：文案移到中间 / 月亮放大 / 多一些中秋元素 / 改成暖金高级 / 文案更正式一点",
    height=110,
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
                selected_model=selected_model,
                show_debug=show_debug,
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
            st.write(f"**Layout:** {LAYOUT_OPTIONS.get(updated_state['layout_mode'], updated_state['layout_mode'])}")
            st.write(f"**Density:** {DENSITY_OPTIONS.get(updated_state['element_density'], updated_state['element_density'])}")
            st.write(f"**Main visual:** {updated_state['main_visual']} / {updated_state['main_visual_position']} / scale {updated_state['main_visual_scale']}")
            st.write(f"**Selected assets:** {', '.join(updated_state['selected_assets'])}")

            with st.expander("Debug JSON"):
                st.json(updated_state)

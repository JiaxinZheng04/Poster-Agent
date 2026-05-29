import io
import json
import math
import random
import re
from copy import deepcopy

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# =========================================================
# GF Securities Poster Agent
# Only Festival Greeting Poster
# =========================================================

st.set_page_config(
    page_title="GF Securities Poster Agent",
    page_icon="🎨",
    layout="wide"
)

# =========================================================
# Basic config
# =========================================================

CANVAS_W = 1080
CANVAS_H = 1350

DEFAULT_SEED = 42
random.seed(DEFAULT_SEED)

# =========================================================
# Data Libraries
# =========================================================

HOLIDAY_LIBRARY = {
    "mid_autumn": {
        "display_name": "中秋节 / Mid-Autumn Festival",
        "tone": "warm, elegant, festive, reunion",
        "default_title": "情满中秋",
        "subtitle_options": [
            "月圆人团圆",
            "佳节共安康",
            "共赏明月，同叙温情"
        ],
        "blessing_options": [
            "广发证券（香港）祝您中秋快乐，阖家团圆，万事顺遂。",
            "愿月圆人圆事事圆满，愿福满情满岁岁安康。",
            "秋光正好，愿您事业顺意，生活圆满。"
        ],
        "asset_pool": ["moon", "rabbit", "cloud", "branch", "water", "city"],
        "background_preferences": ["moonlit_scene", "elegant_gradient", "paper_cut"],
        "style_hint": "warm_gold"
    },
    "spring_festival": {
        "display_name": "春节 / Spring Festival",
        "tone": "joyful, festive, prosperous, warm",
        "default_title": "新春快乐",
        "subtitle_options": [
            "瑞启新程",
            "岁启新篇",
            "万象更新，喜迎新春"
        ],
        "blessing_options": [
            "广发证券（香港）祝您新春大吉，阖家幸福，万事胜意。",
            "愿新岁平安顺遂，财喜盈门，前程似锦。",
            "新岁新禧，愿您所愿皆成，所行皆坦途。"
        ],
        "asset_pool": ["lantern", "ingot", "cloud", "firework", "ribbon", "city"],
        "background_preferences": ["festive_glow", "skyline_celebration", "paper_cut"],
        "style_hint": "red_gold"
    },
    "lantern_festival": {
        "display_name": "元宵节 / Lantern Festival",
        "tone": "warm, bright, festive, reunion",
        "default_title": "元宵喜乐",
        "subtitle_options": [
            "灯月同辉",
            "花灯映春",
            "月满良宵，共启新愿"
        ],
        "blessing_options": [
            "广发证券（香港）祝您元宵快乐，团圆美满，诸事顺遂。",
            "愿灯火可亲，月色长明，喜乐常伴左右。",
            "良宵佳节，愿您平安喜乐，岁岁丰盈。"
        ],
        "asset_pool": ["lantern", "moon", "cloud", "firework", "ribbon", "city"],
        "background_preferences": ["festive_glow", "moonlit_scene", "skyline_celebration"],
        "style_hint": "red_gold"
    },
    "dragon_boat": {
        "display_name": "端午节 / Dragon Boat Festival",
        "tone": "traditional, fresh, festive, blessing",
        "default_title": "端午安康",
        "subtitle_options": [
            "粽香传情",
            "蒲艾迎祥",
            "端阳时节，福至安康"
        ],
        "blessing_options": [
            "广发证券（香港）祝您端午安康，顺遂常伴，平安喜乐。",
            "愿粽香与清风同至，愿安康与好运相随。",
            "端阳佳节，愿您身心安泰，诸事顺意。"
        ],
        "asset_pool": ["wave", "boat", "leaf", "ribbon", "cloud", "city"],
        "background_preferences": ["elegant_gradient", "paper_cut", "geometric_modern"],
        "style_hint": "jade_green"
    },
    "national_day": {
        "display_name": "国庆节 / National Day",
        "tone": "grand, formal, celebratory, uplifting",
        "default_title": "盛世华诞",
        "subtitle_options": [
            "山河锦绣",
            "华章同庆",
            "礼赞祖国，共庆华诞"
        ],
        "blessing_options": [
            "广发证券（香港）祝您国庆快乐，阖家安康，前程锦绣。",
            "愿山河无恙，家国同兴，幸福常在。",
            "共贺盛世，愿生活明朗，事业顺达。"
        ],
        "asset_pool": ["city", "firework", "ribbon", "starburst", "brand_symbol"],
        "background_preferences": ["skyline_celebration", "festive_glow", "geometric_modern"],
        "style_hint": "red_gold"
    },
    "hksar_day": {
        "display_name": "香港特别行政区成立纪念日 / HKSAR Establishment Day",
        "tone": "formal, uplifting, celebratory, official",
        "default_title": "盛世华诞",
        "subtitle_options": [
            "同心同行，共启新程",
            "香江焕彩，同庆盛典",
            "携手并进，共创繁荣"
        ],
        "blessing_options": [
            "广发证券（香港）祝您节日愉快，愿香江繁荣兴盛，诸事顺遂。",
            "同心同庆，愿前路光明，事业顺达，生活安康。",
            "值此纪念日，愿城市欣荣，愿万事皆如所期。"
        ],
        "asset_pool": ["city", "firework", "bauhinia", "ribbon", "starburst", "brand_symbol"],
        "background_preferences": ["skyline_celebration", "geometric_modern", "festive_glow"],
        "style_hint": "warm_gold"
    },
    "christmas": {
        "display_name": "圣诞节 / Christmas",
        "tone": "warm, bright, joyful, festive",
        "default_title": "圣诞快乐",
        "subtitle_options": [
            "温暖圣诞，点亮冬日",
            "佳节欢聚，共迎美好",
            "星光闪耀，圣诞欢欣"
        ],
        "blessing_options": [
            "广发证券（香港）祝您圣诞快乐，平安喜乐，万事皆宜。",
            "愿节日的温暖与祝福陪伴您走向更美好的新岁。",
            "愿铃声与星光送来好运，愿您节日安康、喜乐常在。"
        ],
        "asset_pool": ["tree", "snowflake", "star", "gift", "ribbon", "brand_symbol"],
        "background_preferences": ["winter_night", "festive_glow", "elegant_gradient"],
        "style_hint": "green_red"
    },
    "new_year": {
        "display_name": "元旦 / New Year",
        "tone": "fresh, hopeful, formal, bright",
        "default_title": "元旦新禧",
        "subtitle_options": [
            "岁序更新",
            "新岁启封",
            "新年伊始，共赴新程"
        ],
        "blessing_options": [
            "广发证券（香港）祝您元旦快乐，新年顺遂，前程锦绣。",
            "愿新年带来新的希望与新的收获，万事皆得所愿。",
            "愿时序更迭处，皆有光亮与欢喜。"
        ],
        "asset_pool": ["clock", "starburst", "firework", "ribbon", "city"],
        "background_preferences": ["geometric_modern", "festive_glow", "skyline_celebration"],
        "style_hint": "red_gold"
    },
    "buddha_birthday": {
        "display_name": "佛诞 / Buddha's Birthday",
        "tone": "peaceful, elegant, calm, blessing",
        "default_title": "佛诞吉祥",
        "subtitle_options": [
            "心境澄明，福慧常伴",
            "和光同尘，宁静安然",
            "清净自在，福泽绵长"
        ],
        "blessing_options": [
            "广发证券（香港）祝您佛诞安康，愿心境澄明，福慧常伴。",
            "愿平和与善意常在，愿生活安宁，诸事顺遂。",
            "愿一念清明，一路安宁，所行皆从容。"
        ],
        "asset_pool": ["lotus", "sun", "cloud", "water", "ribbon"],
        "background_preferences": ["elegant_gradient", "paper_cut", "mountain_ink"],
        "style_hint": "soft_ink"
    },
    "chung_yeung": {
        "display_name": "重阳节 / Chung Yeung Festival",
        "tone": "traditional, graceful, reflective, respectful",
        "default_title": "重阳安康",
        "subtitle_options": [
            "登高望远",
            "秋光正好",
            "岁岁重阳，福寿绵长"
        ],
        "blessing_options": [
            "广发证券（香港）祝您重阳安康，平安顺遂，福寿绵长。",
            "愿秋高气爽之时，常有从容与欢喜相伴。",
            "愿心怀明朗，步履坚定，岁岁皆安。"
        ],
        "asset_pool": ["mountain", "sun", "bird", "reed", "cloud"],
        "background_preferences": ["mountain_ink", "elegant_gradient", "paper_cut"],
        "style_hint": "soft_ink"
    },
    "thanksgiving": {
        "display_name": "感恩节 / Thanksgiving",
        "tone": "warm, sincere, thankful, elegant",
        "default_title": "感恩有您",
        "subtitle_options": [
            "心怀感恩，温暖同行",
            "感谢相伴，共赴美好",
            "怀抱感恩，向光而行"
        ],
        "blessing_options": [
            "广发证券（香港）感谢您的支持与信任，祝您感恩节温暖顺意。",
            "愿感恩之心带来温暖与丰盛，愿生活处处有光。",
            "感谢一路同行，愿您喜乐安康，所遇皆美好。"
        ],
        "asset_pool": ["leaf", "ribbon", "starburst", "city", "gift"],
        "background_preferences": ["warm_gradient", "elegant_gradient", "geometric_modern"],
        "style_hint": "warm_gold"
    }
}

VISUAL_STYLES = {
    "auto": {
        "display_name": "Auto based on holiday / 根据节日自动",
        "primary": ["#D8A15D", "#F6E7C8", "#7A4B20"],
        "bg_top": "#F4EFE6",
        "bg_bottom": "#E8D7BD",
        "text_primary": "#5C3616",
        "text_secondary": "#7A5A3C",
        "panel_fill": (255, 248, 238, 180),
        "panel_border": (220, 190, 150, 190)
    },
    "red_gold": {
        "display_name": "红金节庆",
        "primary": ["#B80F18", "#F4E0B8", "#7C0B10"],
        "bg_top": "#C81D25",
        "bg_bottom": "#9E1018",
        "text_primary": "#FFF3D7",
        "text_secondary": "#F3DEB0",
        "panel_fill": (255, 242, 215, 120),
        "panel_border": (255, 225, 180, 170)
    },
    "warm_gold": {
        "display_name": "暖金高级",
        "primary": ["#D8A15D", "#F3EFE2", "#8E5A26"],
        "bg_top": "#E0A547",
        "bg_bottom": "#C98C36",
        "text_primary": "#6D3F18",
        "text_secondary": "#81552B",
        "panel_fill": (250, 241, 221, 145),
        "panel_border": (235, 212, 170, 180)
    },
    "soft_ink": {
        "display_name": "雅致水墨",
        "primary": ["#BCA075", "#F5F2EB", "#4B4134"],
        "bg_top": "#F0EAE0",
        "bg_bottom": "#D7CEC1",
        "text_primary": "#2E2A24",
        "text_secondary": "#61584E",
        "panel_fill": (255, 252, 248, 165),
        "panel_border": (210, 200, 185, 170)
    },
    "jade_green": {
        "display_name": "青翠端雅",
        "primary": ["#2E7D65", "#E9F3EE", "#1E5545"],
        "bg_top": "#66A389",
        "bg_bottom": "#2E7D65",
        "text_primary": "#F4FFF8",
        "text_secondary": "#E1F1E8",
        "panel_fill": (244, 255, 248, 125),
        "panel_border": (190, 225, 210, 180)
    },
    "green_red": {
        "display_name": "圣诞绿红",
        "primary": ["#0F7B63", "#F8F1E3", "#D52B1E"],
        "bg_top": "#EF4136",
        "bg_bottom": "#C21F1A",
        "text_primary": "#FFF5E6",
        "text_secondary": "#FFE8C1",
        "panel_fill": (12, 93, 75, 135),
        "panel_border": (240, 231, 205, 165)
    },
    "modern_blue": {
        "display_name": "现代清爽",
        "primary": ["#2C5F9E", "#EDF5FF", "#163A66"],
        "bg_top": "#6AA7E8",
        "bg_bottom": "#2C5F9E",
        "text_primary": "#F7FBFF",
        "text_secondary": "#E6F1FF",
        "panel_fill": (255, 255, 255, 115),
        "panel_border": (210, 228, 248, 175)
    }
}

LAYOUT_OPTIONS = {
    "auto": "Auto / 自动",
    "center": "Center text / 文案居中",
    "top": "Top text / 文案在上",
    "left": "Left block / 文案偏左",
    "lower": "Lower third / 文案偏下"
}

DENSITY_OPTIONS = {
    "low": "Low / 简洁",
    "medium": "Medium / 适中",
    "high": "High / 丰富"
}

BACKGROUND_TYPES = [
    "moonlit_scene",
    "festive_glow",
    "skyline_celebration",
    "paper_cut",
    "elegant_gradient",
    "winter_night",
    "mountain_ink",
    "geometric_modern",
    "warm_gradient"
]

ALL_ASSETS = sorted(list({
    "moon", "rabbit", "cloud", "branch", "water", "city",
    "lantern", "ingot", "firework", "ribbon", "tree",
    "snowflake", "star", "gift", "clock", "lotus", "sun",
    "mountain", "bird", "reed", "leaf", "wave", "boat",
    "bauhinia", "brand_symbol", "starburst"
}))

# =========================================================
# Font helpers
# =========================================================

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/arphic/ukai.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def get_font(size=32, bold=False):
    candidates = FONT_BOLD_CANDIDATES if bold else FONT_CANDIDATES
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


# =========================================================
# Utility helpers
# =========================================================

def hex_to_rgb(hex_color):
    hex_color = hex_color.replace("#", "").strip()
    if len(hex_color) != 6:
        return (0, 0, 0)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return a + (b - a) * t


def blend_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def wrap_text(text, max_chars=14):
    if not text:
        return []
    lines = []
    current = ""
    for ch in text:
        current += ch
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def draw_vertical_gradient(img, top_hex, bottom_hex):
    top = hex_to_rgb(top_hex)
    bottom = hex_to_rgb(bottom_hex)
    draw = ImageDraw.Draw(img)
    for y in range(img.height):
        t = y / max(1, img.height - 1)
        c = blend_color(top, bottom, t)
        draw.line([(0, y), (img.width, y)], fill=c)


def draw_radial_glow(base, center, radius, color=(255, 255, 255), alpha=120):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    cx, cy = center
    for r in range(radius, 0, -8):
        a = int(alpha * (r / radius) ** 2)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, a))
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    base.alpha_composite(glow)


def draw_noise_overlay(base, opacity=18):
    noise = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(noise)
    step = 8
    for x in range(0, base.width, step):
        for y in range(0, base.height, step):
            val = random.randint(0, opacity)
            draw.point((x, y), fill=(255, 255, 255, val))
    noise = noise.filter(ImageFilter.GaussianBlur(0.4))
    base.alpha_composite(noise)


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def mask_key(key):
    if not key:
        return "(missing)"
    if len(key) <= 10:
        return key[:3] + "..." + key[-2:]
    return key[:5] + "..." + key[-4:]


def safe_get(d, k, default=None):
    return d[k] if isinstance(d, dict) and k in d else default


# =========================================================
# Provider / LLM helpers
# =========================================================

def load_provider_catalog():
    """
    Read provider config from st.secrets.
    Supports OpenAI-compatible chat completion endpoints.

    Example secrets.toml:

    [OPENROUTER]
    api_key = "sk-or-xxxx"
    base_url = "https://openrouter.ai/api/v1"
    model = "openai/gpt-4o-mini"

    [SILICONFLOW]
    api_key = "sk-xxxx"
    base_url = "https://api.siliconflow.cn/v1"
    model = "Qwen/Qwen2.5-7B-Instruct"

    [DEEPSEEK]
    api_key = "sk-xxxx"
    base_url = "https://api.deepseek.com"
    model = "deepseek-chat"

    [ARK]
    api_key = "xxxx"
    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    model = "ep-xxxx"

    [CUSTOM]
    api_key = "xxxx"
    base_url = "https://your-openai-compatible-endpoint/v1"
    model = "your-model"
    """
    providers = {}

    for provider_name in ["OPENROUTER", "SILICONFLOW", "DEEPSEEK", "ARK", "CUSTOM"]:
        if provider_name in st.secrets:
            cfg = st.secrets[provider_name]
            api_key = cfg.get("api_key", "").strip()
            base_url = cfg.get("base_url", "").strip()
            model = cfg.get("model", "").strip()
            if api_key and base_url and model:
                providers[provider_name] = {
                    "label": provider_name.title(),
                    "api_key": api_key,
                    "base_url": base_url.rstrip("/"),
                    "model": model
                }

    return providers


def build_endpoint(base_url):
    if base_url.endswith("/chat/completions"):
        return base_url
    if base_url.endswith("/v1"):
        return f"{base_url}/chat/completions"
    return f"{base_url}/chat/completions"


def extract_json_from_text(text):
    if not text:
        raise ValueError("Empty model response")

    text = text.strip()

    # 1) direct json
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2) fenced json
    fenced = re.findall(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if fenced:
        for item in fenced:
            try:
                return json.loads(item)
            except Exception:
                continue

    # 3) any fenced block
    fenced_any = re.findall(r"```\s*(\{.*?\})\s*```", text, flags=re.S)
    if fenced_any:
        for item in fenced_any:
            try:
                return json.loads(item)
            except Exception:
                continue

    # 4) first { ... last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except Exception as e:
            raise ValueError(f"JSON parse failed: {e}")

    raise ValueError(f"No JSON found in model response: {text[:200]}")


def choose_provider(provider_choice, catalog):
    if not catalog:
        return None, None

    if provider_choice == "Auto":
        # priority
        for k in ["OPENROUTER", "SILICONFLOW", "DEEPSEEK", "ARK", "CUSTOM"]:
            if k in catalog:
                return k, catalog[k]
        first_key = list(catalog.keys())[0]
        return first_key, catalog[first_key]

    if provider_choice in catalog:
        return provider_choice, catalog[provider_choice]

    return None, None


def call_openai_compatible_chat(provider_name, cfg, user_prompt, system_prompt, model_override=""):
    model_name = model_override.strip() if model_override.strip() else cfg["model"]
    endpoint = build_endpoint(cfg["base_url"])

    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json"
    }

    # OpenRouter optional headers
    if provider_name == "OPENROUTER":
        headers["HTTP-Referer"] = "https://streamlit.app"
        headers["X-Title"] = "GF Securities Poster Agent"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 900
    }

    r = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    return {
        "provider": provider_name,
        "model": model_name,
        "base_url": cfg["base_url"],
        "raw": content,
        "response_json": data
    }


def build_llm_prompts(base_state, holiday_info, instruction):
    allowed_assets = ", ".join(ALL_ASSETS)
    allowed_backgrounds = ", ".join(BACKGROUND_TYPES)
    allowed_layouts = ", ".join(LAYOUT_OPTIONS.keys())
    allowed_density = ", ".join(DENSITY_OPTIONS.keys())
    style_name = base_state.get("visual_style", "auto")

    system_prompt = """
You are a senior art director and copywriter for GF Securities (Hong Kong).
Your job is to revise a festival greeting poster specification.

Important:
1. Return ONLY valid JSON.
2. Do not use markdown fences.
3. Write Chinese copy unless the user explicitly asks otherwise.
4. Keep tone client-facing, polished, professional, and not too cliché.
5. Be more creative with background and asset selection, but only choose from the allowed lists.
6. If the user asks for background or atmosphere changes, reflect them via:
   - background_type
   - selected_assets
   - main_visual
   - layout_mode
   - element_density
   - text_panel_style
7. If the user asks for text placement changes, honor them.
8. If the user asks to enrich the visual, select more suitable symbolic assets.
9. If the user asks for official style, use concise and dignified copy.
10. Return a compact JSON object with these keys:
{
  "title": str,
  "subtitle": str,
  "blessing": str,
  "background_type": str,
  "selected_assets": [str, ...],
  "layout_mode": str,
  "element_density": str,
  "text_panel_style": str,
  "main_visual": str,
  "scale_hint": float
}
"""

    user_prompt = f"""
Current holiday:
{holiday_info['display_name']}

Holiday tone:
{holiday_info.get('tone', '')}

Current poster state:
{json.dumps(base_state, ensure_ascii=False, indent=2)}

User instruction:
{instruction if instruction.strip() else "请在当前基础上做更精致、更有节日氛围的优化。"}

Allowed backgrounds:
{allowed_backgrounds}

Allowed assets:
{allowed_assets}

Allowed layout_mode values:
{allowed_layouts}

Allowed element_density values:
{allowed_density}

Current style key:
{style_name}

Notes:
- title should be short, strong, and suitable as the main headline.
- subtitle can be one short line.
- blessing can be one short paragraph, not too long.
- selected_assets length: normally 3 to 6.
- main_visual should be one asset from allowed assets.
- scale_hint should be a float between 0.9 and 1.3.
- text_panel_style can be one of:
  "soft_card", "glass_card", "none", "top_banner", "center_card", "left_block"

Return JSON only.
"""
    return system_prompt, user_prompt


def sanitize_llm_patch(patch, holiday_info):
    if not isinstance(patch, dict):
        return {}

    clean = {}

    if isinstance(patch.get("title"), str) and patch["title"].strip():
        clean["title"] = patch["title"].strip()[:28]

    if isinstance(patch.get("subtitle"), str) and patch["subtitle"].strip():
        clean["subtitle"] = patch["subtitle"].strip()[:40]

    if isinstance(patch.get("blessing"), str) and patch["blessing"].strip():
        clean["blessing"] = patch["blessing"].strip()[:90]

    if patch.get("background_type") in BACKGROUND_TYPES:
        clean["background_type"] = patch["background_type"]

    if patch.get("layout_mode") in LAYOUT_OPTIONS:
        clean["layout_mode"] = patch["layout_mode"]

    if patch.get("element_density") in DENSITY_OPTIONS:
        clean["element_density"] = patch["element_density"]

    if isinstance(patch.get("text_panel_style"), str):
        style = patch["text_panel_style"].strip()
        if style in ["soft_card", "glass_card", "none", "top_banner", "center_card", "left_block"]:
            clean["text_panel_style"] = style

    if patch.get("main_visual") in ALL_ASSETS:
        clean["main_visual"] = patch["main_visual"]

    if isinstance(patch.get("selected_assets"), list):
        filtered = [a for a in patch["selected_assets"] if a in ALL_ASSETS]
        if filtered:
            clean["selected_assets"] = filtered[:6]

    try:
        scale_hint = float(patch.get("scale_hint", 1.0))
        clean["scale_hint"] = max(0.9, min(1.3, scale_hint))
    except Exception:
        pass

    return clean


# =========================================================
# State generation
# =========================================================

def auto_style_for_holiday(holiday_key):
    holiday = HOLIDAY_LIBRARY.get(holiday_key, {})
    return holiday.get("style_hint", "warm_gold")


def auto_background_for_holiday(holiday_key):
    holiday = HOLIDAY_LIBRARY.get(holiday_key, {})
    prefs = holiday.get("background_preferences", ["elegant_gradient"])
    return random.choice(prefs)


def pick_assets(holiday_key, density="medium"):
    holiday = HOLIDAY_LIBRARY.get(holiday_key, {})
    pool = holiday.get("asset_pool", ["cloud", "ribbon", "brand_symbol"])

    if density == "low":
        n = min(3, len(pool))
    elif density == "high":
        n = min(6, len(pool))
    else:
        n = min(4, len(pool))

    if len(pool) <= n:
        return pool
    return random.sample(pool, n)


def choose_main_visual(selected_assets, holiday_key):
    priority = {
        "mid_autumn": ["moon", "rabbit", "city"],
        "spring_festival": ["lantern", "ingot", "city"],
        "lantern_festival": ["lantern", "moon", "city"],
        "dragon_boat": ["boat", "wave", "leaf"],
        "national_day": ["city", "firework", "ribbon"],
        "hksar_day": ["city", "bauhinia", "firework"],
        "christmas": ["tree", "gift", "star"],
        "new_year": ["clock", "firework", "city"],
        "buddha_birthday": ["lotus", "sun", "cloud"],
        "chung_yeung": ["mountain", "sun", "reed"],
        "thanksgiving": ["leaf", "gift", "ribbon"]
    }
    prefs = priority.get(holiday_key, [])
    for item in prefs:
        if item in selected_assets:
            return item
    return selected_assets[0] if selected_assets else "brand_symbol"


def generate_base_state(holiday_key, style_key, layout_mode, element_density, reserve_qr):
    holiday = HOLIDAY_LIBRARY[holiday_key]

    if style_key == "auto":
        resolved_style_key = auto_style_for_holiday(holiday_key)
    else:
        resolved_style_key = style_key

    style = VISUAL_STYLES.get(resolved_style_key, VISUAL_STYLES["warm_gold"])

    selected_assets = pick_assets(holiday_key, element_density if element_density != "auto" else "medium")
    main_visual = choose_main_visual(selected_assets, holiday_key)

    state = {
        "poster_type": "festival_greeting",
        "holiday_key": holiday_key,
        "holiday_name": holiday["display_name"],
        "visual_style": resolved_style_key,
        "colors": style["primary"],
        "tone": holiday.get("tone", "warm, festive"),
        "title": holiday.get("default_title", "节日快乐"),
        "subtitle": random.choice(holiday.get("subtitle_options", ["佳节安康"])),
        "blessing": random.choice(holiday.get("blessing_options", ["广发证券（香港）祝您节日快乐。"])),
        "selected_assets": selected_assets,
        "main_visual": main_visual,
        "background_type": auto_background_for_holiday(holiday_key),
        "layout_mode": "center" if layout_mode == "auto" else layout_mode,
        "element_density": "medium" if element_density == "auto" else element_density,
        "text_panel_style": "center_card",
        "scale_hint": 1.0,
        "reserve_qr": reserve_qr
    }
    return state


def merge_state(base_state, patch):
    new_state = deepcopy(base_state)
    for k, v in patch.items():
        new_state[k] = v
    return new_state


# =========================================================
# Drawing primitives
# =========================================================

def draw_brand_header(img, style):
    draw = ImageDraw.Draw(img)
    font_brand_cn = get_font(44, bold=True)
    font_brand_en = get_font(18, bold=False)

    x = 70
    y = 50

    # simple brand symbol
    draw.rounded_rectangle([x, y, x+50, y+28], radius=10, outline=style["text_secondary"], width=4)
    draw.text((x+62, y-6), "廣發證券（香港）", font=font_brand_cn, fill=style["text_primary"])
    draw.text((x+62, y+38), "GF SECURITIES (HONG KONG)", font=font_brand_en, fill=style["text_secondary"])


def draw_qr_placeholder(img):
    draw = ImageDraw.Draw(img)
    box = [img.width - 210, img.height - 210, img.width - 60, img.height - 60]
    draw.rounded_rectangle(box, radius=16, fill=(255, 255, 255, 235), outline=(220, 220, 220, 255), width=3)

    inner = 24
    x1, y1, x2, y2 = box
    for ox, oy in [(x1+inner, y1+inner), (x2-60-inner, y1+inner), (x1+inner, y2-60-inner)]:
        draw.rectangle([ox, oy, ox+36, oy+36], outline=(60, 60, 60, 255), width=4)
    draw.text((x1+28, y2-42), "QR", font=get_font(24, bold=True), fill=(90, 90, 90, 255))


def draw_moon(draw, center, r, fill=(245, 231, 184, 255)):
    cx, cy = center
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)


def draw_cloud(draw, x, y, scale=1.0, fill=(255, 248, 236, 180)):
    r = 28 * scale
    draw.ellipse([x, y, x+r*1.2, y+r], fill=fill)
    draw.ellipse([x+r*0.55, y-r*0.35, x+r*1.8, y+r*0.8], fill=fill)
    draw.ellipse([x+r*1.15, y, x+r*2.3, y+r], fill=fill)
    draw.rounded_rectangle([x+r*0.15, y+r*0.25, x+r*2.05, y+r*1.05], radius=12, fill=fill)


def draw_rabbit(draw, x, y, scale=1.0, fill=(220, 185, 90, 255)):
    body_w = 130 * scale
    body_h = 110 * scale
    head_r = 38 * scale
    draw.ellipse([x, y, x+body_w, y+body_h], fill=fill)
    draw.ellipse([x+body_w*0.25, y-50*scale, x+body_w*0.25+head_r*2, y-50*scale+head_r*2], fill=fill)
    draw.ellipse([x+body_w*0.35, y-105*scale, x+body_w*0.35+20*scale, y-35*scale], fill=fill)
    draw.ellipse([x+body_w*0.53, y-110*scale, x+body_w*0.53+20*scale, y-38*scale], fill=fill)


def draw_branch(draw, x, y, scale=1.0, fill=(105, 75, 35, 255)):
    points = [(x, y), (x+160*scale, y+30*scale), (x+280*scale, y+80*scale)]
    draw.line(points, fill=fill, width=max(2, int(6*scale)))
    for px, py in [(x+100*scale, y+18*scale), (x+180*scale, y+40*scale), (x+230*scale, y+60*scale)]:
        draw.ellipse([px-10*scale, py-8*scale, px+10*scale, py+8*scale], fill=(140, 95, 55, 255))


def draw_water(draw, y, color=(244, 233, 201, 100)):
    for i in range(7):
        yy = y + i * 14
        draw.arc([80, yy, CANVAS_W-80, yy+80], start=10, end=170, fill=color, width=2)


def draw_city(draw, y_base, color=(140, 55, 55, 170), scale=1.0):
    widths = [70, 85, 60, 95, 72, 105, 64]
    heights = [170, 240, 200, 310, 215, 260, 190]
    x = 110
    gap = 22
    for w, h in zip(widths, heights):
        ww = int(w * scale)
        hh = int(h * scale)
        draw.rectangle([x, y_base-hh, x+ww, y_base], fill=color)
        x += ww + gap


def draw_firework(draw, center, r=60, color=(255, 242, 214, 220)):
    cx, cy = center
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        x2 = cx + r * math.cos(rad)
        y2 = cy + r * math.sin(rad)
        draw.line([cx, cy, x2, y2], fill=color, width=3)
    draw.ellipse([cx-8, cy-8, cx+8, cy+8], fill=color)


def draw_ribbon(draw, x, y, w=240, h=28, color=(215, 160, 93, 180)):
    draw.polygon([(x, y), (x+w, y), (x+w-20, y+h), (x+20, y+h)], fill=color)


def draw_lantern(draw, x, y, scale=1.0, fill=(230, 70, 60, 255)):
    w = 90 * scale
    h = 120 * scale
    draw.ellipse([x, y, x+w, y+h], fill=fill)
    draw.line([x+w/2, y-20*scale, x+w/2, y], fill=(230, 210, 150, 255), width=3)
    draw.line([x+w/2, y+h, x+w/2, y+h+28*scale], fill=(230, 210, 150, 255), width=3)
    for i in range(1, 4):
        draw.line([x+w*i/4, y+15*scale, x+w*i/4, y+h-15*scale], fill=(255, 200, 170, 150), width=2)


def draw_ingot(draw, x, y, scale=1.0, fill=(233, 192, 72, 255)):
    w = 100 * scale
    h = 55 * scale
    draw.pieslice([x, y, x+w, y+h], start=0, end=180, fill=fill)
    draw.ellipse([x+w*0.25, y+h*0.2, x+w*0.75, y+h*0.7], fill=(245, 215, 120, 255))


def draw_tree(draw, x, y, scale=1.0):
    green = (30, 130, 100, 255)
    gold = (245, 219, 159, 255)
    draw.polygon([(x, y+160*scale), (x+110*scale, y), (x+220*scale, y+160*scale)], fill=green)
    draw.polygon([(x+20*scale, y+245*scale), (x+110*scale, y+75*scale), (x+200*scale, y+245*scale)], fill=green)
    draw.rectangle([x+90*scale, y+245*scale, x+130*scale, y+315*scale], fill=(115, 70, 45, 255))
    draw.ellipse([x+100*scale-14, y-28*scale, x+100*scale+14, y,], fill=gold)


def draw_snowflake(draw, x, y, scale=1.0, fill=(255, 255, 255, 220)):
    r = 24 * scale
    for ang in range(0, 180, 30):
        rad = math.radians(ang)
        x2 = x + r * math.cos(rad)
        y2 = y + r * math.sin(rad)
        x3 = x - r * math.cos(rad)
        y3 = y - r * math.sin(rad)
        draw.line([x, y, x2, y2], fill=fill, width=2)
        draw.line([x, y, x3, y3], fill=fill, width=2)


def draw_star(draw, x, y, scale=1.0, fill=(255, 237, 170, 230)):
    pts = []
    r1 = 24 * scale
    r2 = 10 * scale
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = r1 if i % 2 == 0 else r2
        pts.append((x + r * math.cos(ang), y + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def draw_gift(draw, x, y, scale=1.0):
    w = 120 * scale
    h = 100 * scale
    draw.rectangle([x, y, x+w, y+h], fill=(238, 236, 225, 255))
    draw.rectangle([x+w*0.46, y, x+w*0.54, y+h], fill=(220, 80, 80, 255))
    draw.rectangle([x, y+h*0.46, x+w, y+h*0.54], fill=(220, 80, 80, 255))


def draw_clock(draw, x, y, scale=1.0):
    r = 160 * scale
    draw.ellipse([x-r, y-r, x+r, y+r], outline=(255, 242, 214, 210), width=8)
    for i in range(12):
        ang = math.radians(-90 + i * 30)
        x1 = x + (r-18) * math.cos(ang)
        y1 = y + (r-18) * math.sin(ang)
        x2 = x + r * math.cos(ang)
        y2 = y + r * math.sin(ang)
        draw.line([x1, y1, x2, y2], fill=(255, 242, 214, 210), width=3)
    draw.line([x, y, x, y-r*0.58], fill=(255, 242, 214, 230), width=6)
    draw.line([x, y, x+r*0.42, y], fill=(255, 242, 214, 230), width=5)
    draw.ellipse([x-10, y-10, x+10, y+10], fill=(255, 242, 214, 255))


def draw_lotus(draw, x, y, scale=1.0):
    fill = (239, 223, 185, 255)
    petals = [
        [x, y+50*scale, x+40*scale, y, x+80*scale, y+50*scale],
        [x+45*scale, y+45*scale, x+85*scale, y-8*scale, x+125*scale, y+45*scale],
        [x+90*scale, y+50*scale, x+130*scale, y, x+170*scale, y+50*scale]
    ]
    for p in petals:
        draw.polygon(p, fill=fill)
    draw.ellipse([x+50*scale, y+30*scale, x+120*scale, y+75*scale], fill=(232, 204, 139, 255))


def draw_sun(draw, x, y, scale=1.0):
    r = 45 * scale
    draw.ellipse([x-r, y-r, x+r, y+r], fill=(247, 207, 124, 240))
    for ang in range(0, 360, 20):
        rad = math.radians(ang)
        x2 = x + (r+35*scale) * math.cos(rad)
        y2 = y + (r+35*scale) * math.sin(rad)
        draw.line([x, y, x2, y2], fill=(247, 225, 170, 190), width=3)


def draw_mountain(draw, x, y, scale=1.0, fill=(190, 180, 165, 150)):
    draw.polygon([(x, y), (x+160*scale, y-190*scale), (x+300*scale, y)], fill=fill)
    draw.polygon([(x+180*scale, y), (x+340*scale, y-160*scale), (x+500*scale, y)], fill=fill)


def draw_bird(draw, x, y, scale=1.0, fill=(90, 90, 90, 180)):
    draw.arc([x, y, x+35*scale, y+20*scale], 200, 340, fill=fill, width=2)
    draw.arc([x+25*scale, y, x+60*scale, y+20*scale], 200, 340, fill=fill, width=2)


def draw_reed(draw, x, y, scale=1.0, fill=(210, 185, 145, 200)):
    for i in range(4):
        dx = i * 20 * scale
        draw.line([x+dx, y, x+dx-20*scale, y-180*scale], fill=fill, width=3)
        draw.ellipse([x+dx-35*scale, y-220*scale, x+dx+5*scale, y-160*scale], fill=fill)


def draw_leaf(draw, x, y, scale=1.0, fill=(210, 142, 74, 230)):
    draw.polygon([(x, y+50*scale), (x+50*scale, y), (x+100*scale, y+50*scale), (x+50*scale, y+100*scale)], fill=fill)
    draw.line([x+50*scale, y+5*scale, x+50*scale, y+95*scale], fill=(180, 105, 50, 230), width=3)


def draw_wave(draw, x, y, scale=1.0, fill=(230, 245, 238, 200)):
    for i in range(4):
        draw.arc([x, y+i*24, x+360*scale, y+90*scale+i*24], start=0, end=180, fill=fill, width=3)


def draw_boat(draw, x, y, scale=1.0, fill=(54, 104, 85, 255)):
    draw.polygon([(x, y), (x+160*scale, y), (x+130*scale, y+40*scale), (x+20*scale, y+40*scale)], fill=fill)
    draw.line([x+70*scale, y, x+70*scale, y-90*scale], fill=fill, width=4)
    draw.polygon([(x+70*scale, y-90*scale), (x+140*scale, y-40*scale), (x+70*scale, y-10*scale)], fill=(222, 235, 226, 240))


def draw_bauhinia(draw, x, y, scale=1.0, fill=(255, 242, 214, 220)):
    for i in range(5):
        ang = math.radians(i * 72 - 90)
        px = x + 55 * scale * math.cos(ang)
        py = y + 55 * scale * math.sin(ang)
        draw.ellipse([px-30*scale, py-18*scale, px+30*scale, py+18*scale], fill=fill)
    draw.ellipse([x-12*scale, y-12*scale, x+12*scale, y+12*scale], fill=(245, 220, 170, 240))


def draw_brand_symbol(draw, x, y, scale=1.0, color=(255, 241, 216, 230)):
    draw.rounded_rectangle([x, y, x+70*scale, y+40*scale], radius=14, outline=color, width=4)
    draw.arc([x+14*scale, y+8*scale, x+66*scale, y+50*scale], 210, 340, fill=color, width=4)


def draw_starburst(draw, x, y, scale=1.0, fill=(255, 242, 214, 220)):
    for ang in range(0, 360, 12):
        rad = math.radians(ang)
        x2 = x + 48 * scale * math.cos(rad)
        y2 = y + 48 * scale * math.sin(rad)
        draw.line([x, y, x2, y2], fill=fill, width=2)
    draw.ellipse([x-10*scale, y-10*scale, x+10*scale, y+10*scale], fill=fill)


# =========================================================
# Background / asset renderer
# =========================================================

def render_background(img, state, style):
    bg = state.get("background_type", "elegant_gradient")

    if bg == "moonlit_scene":
        draw_vertical_gradient(img, "#B83A2E", "#9A2E24" if state["visual_style"] == "red_gold" else "#D59A4B")
        draw_radial_glow(img, (img.width // 2, 460), 300, color=(255, 245, 210), alpha=80)
    elif bg == "festive_glow":
        draw_vertical_gradient(img, style["bg_top"], style["bg_bottom"])
        draw_radial_glow(img, (img.width * 3 // 4, 220), 260, color=(255, 235, 190), alpha=90)
        draw_radial_glow(img, (180, 260), 200, color=(255, 210, 160), alpha=50)
    elif bg == "skyline_celebration":
        draw_vertical_gradient(img, style["bg_top"], style["bg_bottom"])
        draw_radial_glow(img, (img.width//2, 250), 320, color=(255, 226, 170), alpha=60)
    elif bg == "paper_cut":
        draw_vertical_gradient(img, style["bg_top"], style["bg_bottom"])
    elif bg == "winter_night":
        draw_vertical_gradient(img, "#D73B30", "#AD2019")
        draw_radial_glow(img, (img.width//2, 300), 260, color=(255, 248, 220), alpha=35)
    elif bg == "mountain_ink":
        draw_vertical_gradient(img, "#F3EDE3", "#DACEBF")
    elif bg == "geometric_modern":
        draw_vertical_gradient(img, style["bg_top"], style["bg_bottom"])
    elif bg == "warm_gradient":
        draw_vertical_gradient(img, "#F0C67A", "#D69845")
    else:
        draw_vertical_gradient(img, style["bg_top"], style["bg_bottom"])

    draw_noise_overlay(img, opacity=10)

    # extra geometric layers for some backgrounds
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    if bg == "geometric_modern":
        odraw.polygon([(0, 260), (520, 260), (360, 620), (0, 620)], fill=(255, 255, 255, 25))
        odraw.polygon([(720, 120), (1080, 120), (1080, 560), (820, 560)], fill=(255, 255, 255, 18))
        odraw.arc([60, 100, 620, 660], 0, 270, fill=(255, 255, 255, 35), width=3)
        odraw.arc([90, 130, 590, 630], 0, 270, fill=(255, 255, 255, 25), width=3)

    if bg == "paper_cut":
        odraw.ellipse([120, 230, 920, 1030], fill=(255, 247, 225, 28))
        odraw.arc([180, 290, 860, 980], 0, 360, fill=(255, 248, 230, 55), width=2)
        odraw.arc([240, 350, 800, 920], 0, 360, fill=(255, 248, 230, 45), width=2)

    if bg == "mountain_ink":
        odraw.ellipse([680, 120, 880, 320], fill=(236, 200, 145, 150))

    img.alpha_composite(overlay)


def render_asset(draw, asset, x, y, scale=1.0):
    if asset == "moon":
        draw_moon(draw, (x, y), int(140 * scale), fill=(247, 239, 202, 240))
    elif asset == "rabbit":
        draw_rabbit(draw, x, y, scale=scale)
    elif asset == "cloud":
        draw_cloud(draw, x, y, scale=scale)
    elif asset == "branch":
        draw_branch(draw, x, y, scale=scale)
    elif asset == "water":
        draw_water(draw, y)
    elif asset == "city":
        draw_city(draw, y, scale=scale)
    elif asset == "lantern":
        draw_lantern(draw, x, y, scale=scale)
    elif asset == "ingot":
        draw_ingot(draw, x, y, scale=scale)
    elif asset == "firework":
        draw_firework(draw, (x, y), r=int(52*scale))
    elif asset == "ribbon":
        draw_ribbon(draw, x, y, w=int(280*scale), h=int(28*scale))
    elif asset == "tree":
        draw_tree(draw, x, y, scale=scale)
    elif asset == "snowflake":
        draw_snowflake(draw, x, y, scale=scale)
    elif asset == "star":
        draw_star(draw, x, y, scale=scale)
    elif asset == "gift":
        draw_gift(draw, x, y, scale=scale)
    elif asset == "clock":
        draw_clock(draw, x, y, scale=scale)
    elif asset == "lotus":
        draw_lotus(draw, x, y, scale=scale)
    elif asset == "sun":
        draw_sun(draw, x, y, scale=scale)
    elif asset == "mountain":
        draw_mountain(draw, x, y, scale=scale)
    elif asset == "bird":
        draw_bird(draw, x, y, scale=scale)
    elif asset == "reed":
        draw_reed(draw, x, y, scale=scale)
    elif asset == "leaf":
        draw_leaf(draw, x, y, scale=scale)
    elif asset == "wave":
        draw_wave(draw, x, y, scale=scale)
    elif asset == "boat":
        draw_boat(draw, x, y, scale=scale)
    elif asset == "bauhinia":
        draw_bauhinia(draw, x, y, scale=scale)
    elif asset == "brand_symbol":
        draw_brand_symbol(draw, x, y, scale=scale)
    elif asset == "starburst":
        draw_starburst(draw, x, y, scale=scale)


def render_main_visual(draw, state):
    main_visual = state.get("main_visual", "brand_symbol")
    scale_hint = float(state.get("scale_hint", 1.0))
    bg = state.get("background_type", "elegant_gradient")

    # main visual placement
    if state.get("layout_mode") == "top":
        hero_y = 640
    elif state.get("layout_mode") == "lower":
        hero_y = 460
    else:
        hero_y = 620

    if main_visual == "moon":
        render_asset(draw, "moon", CANVAS_W // 2, hero_y, scale=1.25 * scale_hint)
        render_asset(draw, "rabbit", CANVAS_W // 2 - 80, hero_y + 130, scale=1.0)
        render_asset(draw, "cloud", CANVAS_W // 2 + 90, hero_y + 90, scale=1.4)
    elif main_visual == "city":
        render_asset(draw, "city", 0, CANVAS_H - 330, scale=1.15 * scale_hint)
    elif main_visual == "clock":
        render_asset(draw, "clock", CANVAS_W // 2, 490, scale=1.0 * scale_hint)
    elif main_visual == "tree":
        render_asset(draw, "tree", CANVAS_W // 2 - 160, 420, scale=1.3 * scale_hint)
    elif main_visual == "lotus":
        render_asset(draw, "lotus", CANVAS_W // 2 - 120, 500, scale=1.35 * scale_hint)
        render_asset(draw, "sun", CANVAS_W // 2, 390, scale=1.15)
    elif main_visual == "mountain":
        render_asset(draw, "mountain", 180, 820, scale=1.3)
        render_asset(draw, "sun", 820, 280, scale=1.05)
    elif main_visual == "lantern":
        render_asset(draw, "lantern", CANVAS_W // 2 - 70, 430, scale=1.8 * scale_hint)
    elif main_visual == "boat":
        render_asset(draw, "wave", 220, 700, scale=1.7)
        render_asset(draw, "boat", CANVAS_W // 2 - 100, 680, scale=1.3 * scale_hint)
    elif main_visual == "bauhinia":
        render_asset(draw, "bauhinia", CANVAS_W // 2, 520, scale=1.8 * scale_hint)
        render_asset(draw, "city", 0, CANVAS_H - 340, scale=1.05)
    else:
        render_asset(draw, main_visual, CANVAS_W // 2 - 60, 500, scale=1.4 * scale_hint)


def render_supporting_assets(draw, state):
    assets = state.get("selected_assets", [])
    density = state.get("element_density", "medium")
    layout = state.get("layout_mode", "center")
    bg = state.get("background_type", "")

    # fewer duplicates around main visual
    supplemental = [a for a in assets if a != state.get("main_visual")]
    max_items = 2 if density == "low" else 4 if density == "medium" else 6
    supplemental = supplemental[:max_items]

    positions = [
        ("top_left", 120, 200, 0.9),
        ("top_right", 860, 220, 0.9),
        ("mid_left", 120, 560, 0.95),
        ("mid_right", 900, 560, 0.95),
        ("bottom_left", 160, 1090, 0.9),
        ("bottom_right", 860, 1090, 0.9),
    ]

    for asset, (_, x, y, s) in zip(supplemental, positions):
        # minor placement rules
        if asset == "city":
            render_asset(draw, asset, 0, CANVAS_H - 300, scale=0.8)
        elif asset == "water":
            render_asset(draw, asset, 0, 980, scale=1.0)
        elif asset == "mountain":
            render_asset(draw, asset, 70, 920, scale=0.8)
        elif asset in ["firework", "starburst", "snowflake", "star", "bird"]:
            render_asset(draw, asset, x, y, scale=s)
        else:
            render_asset(draw, asset, x-50, y-50, scale=s)


# =========================================================
# Text renderer
# =========================================================

def draw_text_panel(draw, state, style):
    layout = state.get("layout_mode", "center")
    panel_style = state.get("text_panel_style", "center_card")

    title = state.get("title", "")
    subtitle = state.get("subtitle", "")
    blessing = state.get("blessing", "")

    title_font = get_font(84, bold=True)
    sub_font = get_font(32, bold=True)
    body_font = get_font(28, bold=False)

    text_primary = style["text_primary"]
    text_secondary = style["text_secondary"]

    if layout == "center":
        panel = [130, 470, CANVAS_W - 130, 760]
    elif layout == "top":
        panel = [100, 190, CANVAS_W - 100, 470]
    elif layout == "left":
        panel = [80, 390, 580, 760]
    elif layout == "lower":
        panel = [120, 760, CANVAS_W - 120, 1040]
    else:
        panel = [130, 470, CANVAS_W - 130, 760]

    if panel_style != "none":
        fill = style["panel_fill"]
        outline = style["panel_border"]

        if panel_style == "glass_card":
            fill = (255, 255, 255, 105)
        elif panel_style == "top_banner":
            panel = [70, 155, CANVAS_W - 70, 455]
        elif panel_style == "left_block":
            panel = [70, 380, 540, 790]
        elif panel_style == "soft_card":
            pass

        rounded_rect(draw, panel, radius=28, fill=fill, outline=outline, width=2)

    px1, py1, px2, py2 = panel
    center_x = (px1 + px2) // 2
    cur_y = py1 + 36

    # title
    title_lines = wrap_text(title, 10 if layout != "left" else 8)
    for line in title_lines[:2]:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = center_x - tw // 2 if layout != "left" else px1 + 36
        draw.text((tx, cur_y), line, font=title_font, fill=text_primary)
        cur_y += 92

    # subtitle
    if subtitle:
        subtitle_lines = wrap_text(subtitle, 16 if layout != "left" else 12)
        for line in subtitle_lines[:1]:
            bbox = draw.textbbox((0, 0), line, font=sub_font)
            tw = bbox[2] - bbox[0]
            tx = center_x - tw // 2 if layout != "left" else px1 + 36
            draw.text((tx, cur_y), line, font=sub_font, fill=text_primary)
            cur_y += 52

    # blessing
    if blessing:
        cur_y += 8
        blessing_lines = wrap_text(blessing, 20 if layout != "left" else 13)
        for line in blessing_lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            tw = bbox[2] - bbox[0]
            tx = center_x - tw // 2 if layout != "left" else px1 + 36
            draw.text((tx, cur_y), line, font=body_font, fill=text_secondary)
            cur_y += 38


# =========================================================
# Final poster rendering
# =========================================================

def render_poster(state):
    style = VISUAL_STYLES.get(state["visual_style"], VISUAL_STYLES["warm_gold"])

    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
    render_background(img, state, style)

    draw = ImageDraw.Draw(img)

    draw_brand_header(img, style)
    render_main_visual(draw, state)
    render_supporting_assets(draw, state)
    draw_text_panel(draw, state, style)

    if state.get("reserve_qr", True):
        draw_qr_placeholder(img)

    return img


# =========================================================
# Generation flow
# =========================================================

def generate_with_llm(base_state, instruction, provider_choice, model_override, show_debug):
    catalog = load_provider_catalog()

    provider_name, cfg = choose_provider(provider_choice, catalog)
    if not provider_name or not cfg:
        return {
            "success": False,
            "state": base_state,
            "message": "No valid LLM provider configured in st.secrets. Using rule-based fallback.",
            "debug": {"reason": "missing_provider"},
            "raw": ""
        }

    holiday_info = HOLIDAY_LIBRARY[base_state["holiday_key"]]
    system_prompt, user_prompt = build_llm_prompts(base_state, holiday_info, instruction)

    debug_info = {
        "provider": provider_name,
        "model": model_override.strip() if model_override.strip() else cfg["model"],
        "base_url": cfg["base_url"],
        "api_key": mask_key(cfg["api_key"])
    }

    try:
        result = call_openai_compatible_chat(
            provider_name=provider_name,
            cfg=cfg,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            model_override=model_override
        )

        raw = result["raw"]
        patch = extract_json_from_text(raw)
        patch = sanitize_llm_patch(patch, holiday_info)
        final_state = merge_state(base_state, patch)

        debug_info["raw_model_response"] = raw
        debug_info["patch"] = patch

        return {
            "success": True,
            "state": final_state,
            "message": f"LLM call succeeded: {provider_name}",
            "debug": debug_info,
            "raw": raw
        }

    except Exception as e:
        debug_info["error"] = str(e)
        return {
            "success": False,
            "state": base_state,
            "message": f"LLM call failed. Using rule-based fallback. Error: {e}",
            "debug": debug_info,
            "raw": ""
        }


def build_initial_or_revision_state(holiday_key, style_key, layout_mode, density, reserve_qr):
    # If we already have a current state for the same holiday, use it as base
    if "poster_state" in st.session_state:
        prev = st.session_state.poster_state
        if prev.get("holiday_key") == holiday_key:
            revised = deepcopy(prev)

            # apply sidebar changes
            if style_key == "auto":
                revised["visual_style"] = auto_style_for_holiday(holiday_key)
            else:
                revised["visual_style"] = style_key

            if layout_mode != "auto":
                revised["layout_mode"] = layout_mode
            if density != "auto":
                revised["element_density"] = density

            revised["reserve_qr"] = reserve_qr
            return revised

    return generate_base_state(
        holiday_key=holiday_key,
        style_key=style_key,
        layout_mode=layout_mode,
        element_density=density,
        reserve_qr=reserve_qr
    )


def pil_to_bytes(img):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


# =========================================================
# Sidebar UI
# =========================================================

st.title("🎨 GF Securities Poster Agent")
st.caption("Generate festival greeting posters using controlled company-style assets, with optional LLM-assisted copywriting, layout, and visual direction.")

with st.sidebar:
    st.header("Poster Settings")

    holiday_keys = list(HOLIDAY_LIBRARY.keys())
    holiday_key = st.selectbox(
        "节日主题 / Holiday Theme",
        options=holiday_keys,
        format_func=lambda x: HOLIDAY_LIBRARY[x]["display_name"]
    )

    style_key = st.selectbox(
        "视觉风格 / Visual Style",
        options=list(VISUAL_STYLES.keys()),
        format_func=lambda x: VISUAL_STYLES[x]["display_name"],
        index=0
    )

    layout_mode = st.selectbox(
        "版式 / Layout",
        options=list(LAYOUT_OPTIONS.keys()),
        format_func=lambda x: LAYOUT_OPTIONS[x],
        index=0
    )

    density = st.selectbox(
        "元素密度 / Element density",
        options=["auto", "low", "medium", "high"],
        format_func=lambda x: "Auto / 自动" if x == "auto" else DENSITY_OPTIONS[x],
        index=0
    )

    reserve_qr = st.checkbox("Reserve QR area / 预留二维码位置", value=True)

    st.markdown("---")
    st.header("AI Provider")

    use_llm = st.toggle("Use LLM for copywriting & layout", value=True)

    provider_catalog = load_provider_catalog()
    provider_options = ["Auto"] + list(provider_catalog.keys())

    provider_choice = st.selectbox(
        "Provider",
        options=provider_options,
        format_func=lambda x: "Auto / 自动选择可用 Provider" if x == "Auto" else x,
        index=0
    )

    model_override = st.text_input(
        "Model override（可留空）",
        value="",
        placeholder="Leave empty to use model from secrets"
    )

    show_llm_debug = st.checkbox("Show LLM debug", value=False)

    if provider_catalog:
        selected_provider_name, selected_provider_cfg = choose_provider(provider_choice, provider_catalog)
        if selected_provider_cfg:
            st.success(f"Configured: {selected_provider_name}")
    else:
        st.warning("No provider found in st.secrets yet.")

    st.markdown("---")

    if st.button("Test LLM Connection", use_container_width=True):
        if not use_llm:
            st.info("LLM is currently turned off.")
        else:
            test_state = build_initial_or_revision_state(holiday_key, style_key, layout_mode, density, reserve_qr)
            test_result = generate_with_llm(
                base_state=test_state,
                instruction="请输出一版更正式、更精致的节日文案与版式建议。",
                provider_choice=provider_choice,
                model_override=model_override,
                show_debug=show_llm_debug
            )

            if show_llm_debug:
                dbg = test_result["debug"]
                st.info(
                    f"Trying {dbg.get('provider', '')} | model: {dbg.get('model', '')} | "
                    f"base_url: {dbg.get('base_url', '')} | api_key: {dbg.get('api_key', '')}"
                )

            if test_result["success"]:
                st.success(test_result["message"])
                if show_llm_debug and test_result["raw"]:
                    with st.expander("Raw model response"):
                        st.code(test_result["raw"], language="json")
            else:
                st.error(test_result["message"])
                if show_llm_debug:
                    with st.expander("Debug detail"):
                        st.json(test_result["debug"])

    if st.button("Reset Current Poster", use_container_width=True):
        for k in ["poster_state", "poster_image_bytes", "llm_debug_state"]:
            if k in st.session_state:
                del st.session_state[k]
        st.success("Current poster session reset.")

# =========================================================
# Main UI
# =========================================================

st.markdown("---")
st.subheader("1. Generate Poster")

instruction = st.text_area(
    "输入文案和版式要求 / Copywriting & layout instruction",
    value="",
    height=120,
    placeholder="例如：\n- 面向客户，语气正式一些\n- 背景增加更多香港元素\n- 文案放在图片中间\n- 画面更高级、更有层次，不要太俗套\n- 多一些中秋元素"
)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    generate_clicked = st.button("Generate Poster", use_container_width=True)

if generate_clicked:
    base_state = build_initial_or_revision_state(
        holiday_key=holiday_key,
        style_key=style_key,
        layout_mode=layout_mode,
        density=density,
        reserve_qr=reserve_qr
    )

    llm_result = None
    final_state = base_state

    if use_llm:
        llm_result = generate_with_llm(
            base_state=base_state,
            instruction=instruction,
            provider_choice=provider_choice,
            model_override=model_override,
            show_debug=show_llm_debug
        )
        final_state = llm_result["state"]
        st.session_state.llm_debug_state = llm_result

        if show_llm_debug:
            dbg = llm_result["debug"]
            st.info(
                f"Trying {dbg.get('provider', '')} | model: {dbg.get('model', '')} | "
                f"base_url: {dbg.get('base_url', '')} | api_key: {dbg.get('api_key', '')}"
            )

        if llm_result["success"]:
            st.success(llm_result["message"])
            if show_llm_debug and llm_result["raw"]:
                with st.expander("Raw model response"):
                    st.code(llm_result["raw"], language="json")
        else:
            st.warning(llm_result["message"])
    else:
        st.info("LLM is off. Using rule-based generation only.")

    poster_img = render_poster(final_state)
    poster_bytes = pil_to_bytes(poster_img)

    st.session_state.poster_state = final_state
    st.session_state.poster_image_bytes = poster_bytes

    st.success("Poster generated.")

# =========================================================
# Display output
# =========================================================

if "poster_state" in st.session_state and "poster_image_bytes" in st.session_state:
    poster_state = st.session_state.poster_state
    poster_img_bytes = st.session_state.poster_image_bytes

    c1, c2 = st.columns([3, 2], gap="large")

    with c1:
        st.image(poster_img_bytes, use_container_width=True)
        st.download_button(
            "Download PNG",
            data=poster_img_bytes,
            file_name=f"gf_poster_{poster_state['holiday_key']}.png",
            mime="image/png",
            use_container_width=True
        )

    with c2:
        st.subheader("Generation Summary")
        st.write(f"**Holiday:** {poster_state['holiday_name']}")
        st.write(f"**Visual style:** {VISUAL_STYLES.get(poster_state['visual_style'], {}).get('display_name', poster_state['visual_style'])}")
        st.write(f"**Layout:** {LAYOUT_OPTIONS.get(poster_state.get('layout_mode', 'center'), poster_state.get('layout_mode', 'center'))}")
        st.write(f"**Density:** {DENSITY_OPTIONS.get(poster_state.get('element_density', 'medium'), poster_state.get('element_density', 'medium'))}")
        st.write(f"**Main visual:** {poster_state.get('main_visual', '')}")
        st.write(f"**Selected assets:** {', '.join(poster_state.get('selected_assets', []))}")

        with st.expander("Debug JSON", expanded=False):
            st.json(poster_state)

        if show_llm_debug and "llm_debug_state" in st.session_state:
            with st.expander("LLM Debug", expanded=False):
                st.json(st.session_state.llm_debug_state.get("debug", {}))

else:
    st.info("请在上方选择节日与风格，然后点击 Generate Poster。")

import streamlit as st
import io
import json
import math
import random
import re
from copy import deepcopy

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

st.set_page_config(page_title="GF Securities Poster Agent", page_icon="🎨", layout="wide")

CANVAS_W = 1080
CANVAS_H = 1350

HOLIDAYS = {
    "mid_autumn": {
        "name": "中秋節 / Mid-Autumn Festival",
        "template": "mid_autumn_gold",
        "title": "情滿中秋",
        "subtitle": "月圓人團圓",
        "body": "廣發證券（香港）祝您中秋安康，闔家團圓，萬事順遂。",
        "motifs": ["moon", "rabbit", "clouds", "gold_particles"],
    },
    "spring_festival": {
        "name": "春節 / Chinese New Year",
        "template": "spring_red_gold",
        "title": "恭賀新春",
        "subtitle": "瑞啟新程，萬象更新",
        "body": "廣發證券（香港）祝您新春大吉，闔家幸福，萬事勝意。",
        "motifs": ["lanterns", "fireworks", "ribbons", "gold_particles"],
    },
    "hksar_day": {
        "name": "香港特別行政區成立紀念日 / HKSAR Establishment Day",
        "template": "hksar_formal_gold",
        "title": "香江同慶",
        "subtitle": "同心同行，共啟新程",
        "body": "廣發證券（香港）祝您節日愉快，願香江繁榮穩健，前路順遂。",
        "motifs": ["skyline", "bauhinia", "fireworks", "gold_rays", "gold_particles"],
    },
    "national_day": {
        "name": "國慶日 / National Day",
        "template": "national_red_grand",
        "title": "盛世華誕",
        "subtitle": "山河錦繡，家國同慶",
        "body": "廣發證券（香港）祝您國慶快樂，闔家安康，前程錦繡。",
        "motifs": ["skyline", "fireworks", "gold_rays", "ribbons"],
    },
    "christmas": {
        "name": "聖誕節 / Christmas",
        "template": "christmas_red_green",
        "title": "聖誕快樂",
        "subtitle": "溫暖佳節，共迎美好",
        "body": "廣發證券（香港）祝您聖誕快樂，平安喜樂，萬事皆宜。",
        "motifs": ["tree", "snowflakes", "stars", "gift"],
    },
    "new_year": {
        "name": "元旦 / New Year",
        "template": "new_year_modern",
        "title": "元旦新禧",
        "subtitle": "歲序更新，共赴新程",
        "body": "廣發證券（香港）祝您元旦快樂，新年順遂，前程錦繡。",
        "motifs": ["clock", "fireworks", "gold_rays", "stars"],
    },
    "buddha_birthday": {
        "name": "佛誕 / Buddha's Birthday",
        "template": "ink_elegant",
        "title": "佛誕吉祥",
        "subtitle": "心境澄明，福慧常伴",
        "body": "廣發證券（香港）祝您佛誕安康，願心境澄明，萬事順遂。",
        "motifs": ["lotus", "sun", "clouds", "water"],
    },
    "chung_yeung": {
        "name": "重陽節 / Chung Yeung Festival",
        "template": "ink_mountain",
        "title": "重陽安康",
        "subtitle": "登高望遠，秋意綿長",
        "body": "廣發證券（香港）祝您重陽安康，平安順遂，福壽綿長。",
        "motifs": ["mountain", "sun", "birds", "clouds"],
    },
    "thanksgiving": {
        "name": "感恩節 / Thanksgiving",
        "template": "warm_gold",
        "title": "感恩有您",
        "subtitle": "心懷感恩，溫暖同行",
        "body": "廣發證券（香港）感謝您的支持與信任，祝您感恩節溫暖順意。",
        "motifs": ["leaves", "gold_particles", "ribbons", "stars"],
    },
}

TEMPLATES = {
    "auto": "Auto / 根據節日自動",
    "mid_autumn_gold": "中秋暖金",
    "spring_red_gold": "春節紅金",
    "hksar_formal_gold": "香港紀念日正式金",
    "national_red_grand": "國慶紅金大氣",
    "christmas_red_green": "聖誕紅綠",
    "new_year_modern": "元旦現代",
    "ink_elegant": "水墨雅致",
    "ink_mountain": "重陽山水",
    "warm_gold": "通用暖金",
}

LAYOUTS = {
    "auto": "Auto / 自動",
    "center_card": "Center card / 文案居中卡片",
    "top_title": "Top title / 文案偏上",
    "left_editorial": "Left editorial / 文案偏左",
    "lower_card": "Lower card / 文案偏下",
}

DENSITIES = {"low": "Low / 簡潔", "medium": "Medium / 適中", "high": "High / 豐富"}

ALLOWED_MOTIFS = [
    "moon", "rabbit", "clouds", "gold_particles", "lanterns", "ribbons",
    "fireworks", "skyline", "bauhinia", "gold_rays", "tree", "snowflakes",
    "stars", "gift", "clock", "lotus", "sun", "water", "mountain", "birds", "leaves"
]


def secret_get(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def secret_section_get(section, key, default=""):
    try:
        if section in st.secrets:
            return st.secrets[section].get(key, default)
    except Exception:
        pass
    return default


def mask_key(key):
    if not key:
        return "(missing)"
    return key[:6] + "..." + key[-4:] if len(key) > 12 else key[:3] + "..." + key[-2:]


def get_provider_config(provider_name):
    provider_name = provider_name.upper()
    defaults = {
        "OPENROUTER": {"base_url": "https://openrouter.ai/api/v1", "model": "openrouter/free"},
        "SILICONFLOW": {"base_url": "https://api.siliconflow.cn/v1", "model": "Qwen/Qwen2.5-7B-Instruct"},
        "DEEPSEEK": {"base_url": "https://api.deepseek.com", "model": "deepseek-chat"},
        "ARK": {"base_url": "https://ark.cn-beijing.volces.com/api/v3", "model": ""},
        "CUSTOM": {"base_url": "", "model": ""},
    }
    d = defaults.get(provider_name, {"base_url": "", "model": ""})

    api_key = secret_section_get(provider_name, "api_key", "") or secret_get(f"{provider_name}_API_KEY", "")
    base_url = secret_section_get(provider_name, "base_url", "") or secret_get(f"{provider_name}_BASE_URL", "") or d["base_url"]
    model = secret_section_get(provider_name, "model", "") or secret_get(f"{provider_name}_MODEL", "") or d["model"]

    return {
        "provider": provider_name,
        "api_key": str(api_key).strip(),
        "base_url": str(base_url).strip().rstrip("/"),
        "model": str(model).strip(),
    }


def available_providers():
    out = []
    for name in ["OPENROUTER", "SILICONFLOW", "DEEPSEEK", "ARK", "CUSTOM"]:
        cfg = get_provider_config(name)
        if cfg["api_key"] and cfg["base_url"] and cfg["model"]:
            out.append(name)
    return out


def build_chat_endpoint(base_url):
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    if base_url.endswith("/v1") or base_url.endswith("/api/v3"):
        return base_url + "/chat/completions"
    return base_url + "/chat/completions"


def call_llm(provider_name, model_override, system_prompt, user_prompt, debug=False):
    cfg = get_provider_config(provider_name)
    if model_override.strip():
        cfg["model"] = model_override.strip()

    if not cfg["api_key"] or not cfg["base_url"] or not cfg["model"]:
        raise RuntimeError(
            f"{provider_name} is not configured. api_key={mask_key(cfg['api_key'])}, "
            f"base_url={cfg['base_url']}, model={cfg['model']}"
        )

    headers = {"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json"}
    if provider_name.upper() == "OPENROUTER":
        headers["HTTP-Referer"] = "https://streamlit.app"
        headers["X-Title"] = "GF Securities Poster Agent"

    payload = {
        "model": cfg["model"],
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 0.45,
        "max_tokens": 900,
    }

    if debug:
        st.info(f"Trying {provider_name} | model: {cfg['model']} | base_url: {cfg['base_url']} | api_key: {mask_key(cfg['api_key'])}")

    response = requests.post(build_chat_endpoint(cfg["base_url"]), headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"] or ""
    return {"provider": provider_name, "model": cfg["model"], "content": content, "raw_json": data}


def extract_json(text):
    if not text:
        raise ValueError("Empty model response.")
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    fenced = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    for item in fenced:
        try:
            return json.loads(item)
        except Exception:
            pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start:end + 1])
    raise ValueError("No JSON found in model response.")


def build_prompt(base_spec, instruction):
    system_prompt = (
        "You are a senior corporate poster art director and copywriter for GF Securities (Hong Kong). "
        "Return ONLY valid JSON. No markdown. No explanation. "
        "Use polished Traditional Chinese suitable for Hong Kong clients. "
        "Choose only from the allowed template_key, layout, density, and motifs. "
        "Return exactly this JSON structure: "
        '{"title":"...","subtitle":"...","body":"...","template_key":"...","layout":"...","density":"...","motifs":["..."],"qr_reserved":true}'
    )
    user_prompt = f"""
Current poster spec:
{json.dumps(base_spec, ensure_ascii=False, indent=2)}

User instruction:
{instruction}

Allowed template_key values:
{', '.join(TEMPLATES.keys())}

Allowed layout values:
{', '.join(LAYOUTS.keys())}

Allowed density values:
{', '.join(DENSITIES.keys())}

Allowed motifs:
{', '.join(ALLOWED_MOTIFS)}

Rules:
- If the user asks for Hong Kong elements, use skyline, bauhinia, fireworks, gold_rays.
- If the user asks for text in the middle, use layout = center_card.
- If the user asks for richer background, use density = high.
- If the user asks for cleaner style, use density = low.
- Return valid JSON only.
"""
    return system_prompt, user_prompt


def clean_spec(model_spec, base_spec):
    spec = deepcopy(base_spec)
    if not isinstance(model_spec, dict):
        return spec

    for key, max_len in [("title", 26), ("subtitle", 38), ("body", 85)]:
        if isinstance(model_spec.get(key), str) and model_spec[key].strip():
            spec[key] = model_spec[key].strip()[:max_len]

    if model_spec.get("template_key") in TEMPLATES and model_spec.get("template_key") != "auto":
        spec["template_key"] = model_spec["template_key"]
    if model_spec.get("layout") in LAYOUTS and model_spec.get("layout") != "auto":
        spec["layout"] = model_spec["layout"]
    if model_spec.get("density") in DENSITIES:
        spec["density"] = model_spec["density"]
    if isinstance(model_spec.get("motifs"), list):
        motifs = [m for m in model_spec["motifs"] if m in ALLOWED_MOTIFS]
        if motifs:
            spec["motifs"] = motifs[:7]
    if isinstance(model_spec.get("qr_reserved"), bool):
        spec["qr_reserved"] = model_spec["qr_reserved"]
    return spec


def rule_adjust_spec(spec, instruction):
    spec = deepcopy(spec)
    lower = instruction.lower()

    if any(w in instruction for w in ["中間", "中间", "居中", "中央", "畫面中間", "画面中间"]):
        spec["layout"] = "center_card"
    if any(w in instruction for w in ["上方", "頂部", "顶部"]):
        spec["layout"] = "top_title"
    if any(w in instruction for w in ["左側", "左侧", "偏左"]):
        spec["layout"] = "left_editorial"
    if any(w in instruction for w in ["下方", "底部", "偏下"]):
        spec["layout"] = "lower_card"
    if any(w in instruction for w in ["香港", "香江", "特別行政區", "特别行政区", "成立紀念", "成立纪念"]):
        spec["template_key"] = "hksar_formal_gold"
        spec["motifs"] = ["skyline", "bauhinia", "fireworks", "gold_rays", "gold_particles"]
    if any(w in instruction for w in ["正式", "官方", "大氣", "大气", "莊重", "庄重"]):
        spec["body"] = "廣發證券（香港）謹祝您節日愉快，平安順遂，萬事如意。"
        if spec["holiday_key"] == "hksar_day":
            spec["title"] = "香江同慶"
            spec["subtitle"] = "同心同行，共啟新程"
            spec["body"] = "廣發證券（香港）祝您節日愉快，願香江繁榮穩健，前路順遂。"
    if any(w in instruction for w in ["多一些", "更多", "豐富", "丰富", "元素多", "背景多"]):
        spec["density"] = "high"
    if any(w in instruction for w in ["簡潔", "简洁", "乾淨", "干净", "少一點", "少一点"]):
        spec["density"] = "low"
    if "中秋" in instruction:
        spec["template_key"] = "mid_autumn_gold"
        spec["motifs"] = ["moon", "rabbit", "clouds", "gold_particles"]
    if "聖誕" in instruction or "圣诞" in instruction or "christmas" in lower:
        spec["template_key"] = "christmas_red_green"
        spec["motifs"] = ["tree", "snowflakes", "stars", "gift"]
    return spec


def get_font(size, bold=False):
    regular_fonts = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    bold_fonts = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in bold_fonts if bold else regular_fonts:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def hex_to_rgb(value):
    value = value.replace("#", "")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_gradient(img, top, bottom):
    draw = ImageDraw.Draw(img)
    c1 = hex_to_rgb(top)
    c2 = hex_to_rgb(bottom)
    for y in range(img.height):
        t = y / max(1, img.height - 1)
        draw.line([(0, y), (img.width, y)], fill=blend(c1, c2, t))


def add_glow(img, center, radius, color, alpha=100):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = center
    for r in range(radius, 0, -12):
        a = int(alpha * (r / radius) ** 2)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*color, a))
    overlay = overlay.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(overlay)


def add_noise(img, amount=8):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for _ in range(1800):
        x = random.randint(0, img.width - 1)
        y = random.randint(0, img.height - 1)
        a = random.randint(0, amount)
        draw.point((x, y), fill=(255, 255, 255, a))
    img.alpha_composite(overlay)


def wrap_text(text, max_chars):
    lines = []
    current = ""
    for char in text:
        current += char
        if len(current) >= max_chars:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines


def draw_brand(draw, x, y, light=True):
    color = (245, 224, 180, 235) if light else (170, 135, 82, 235)
    font_cn = get_font(38, bold=True)
    font_en = get_font(16)
    draw.rounded_rectangle([x, y + 8, x + 52, y + 38], radius=12, outline=color, width=4)
    draw.text((x + 66, y), "廣發證券（香港）", font=font_cn, fill=color)
    draw.text((x + 68, y + 42), "GF SECURITIES (HONG KONG)", font=font_en, fill=color)


def draw_firework(draw, x, y, r=60, color=(255, 232, 180, 210)):
    for degree in range(0, 360, 15):
        rad = math.radians(degree)
        x2 = x + r * math.cos(rad)
        y2 = y + r * math.sin(rad)
        draw.line([x, y, x2, y2], fill=color, width=3)
    draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=color)


def draw_skyline(draw, y_base, color=(110, 38, 38, 180)):
    buildings = [(90, 170, 70), (180, 260, 85), (290, 210, 70), (680, 300, 90), (805, 230, 75), (900, 180, 65)]
    for x, h, w in buildings:
        draw.rectangle([x, y_base - h, x + w, y_base], fill=color)
        for yy in range(y_base - h + 20, y_base - 10, 28):
            draw.line([x + 10, yy, x + w - 10, yy], fill=(255, 220, 170, 45), width=1)


def draw_bauhinia(draw, x, y, scale=1.0):
    color = (255, 237, 195, 200)
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        px = x + 55 * scale * math.cos(angle)
        py = y + 55 * scale * math.sin(angle)
        draw.ellipse([px - 32 * scale, py - 18 * scale, px + 32 * scale, py + 18 * scale], fill=color)
    draw.ellipse([x - 11 * scale, y - 11 * scale, x + 11 * scale, y + 11 * scale], fill=color)


def draw_moon(draw, x, y, r):
    draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 242, 202, 235))
    draw.ellipse([x - r * 0.65, y - r * 0.65, x + r * 0.65, y + r * 0.65], fill=(247, 221, 151, 90))


def draw_cloud(draw, x, y, scale=1.0):
    color = (255, 250, 232, 150)
    r = 42 * scale
    draw.ellipse([x, y, x + r * 1.5, y + r], fill=color)
    draw.ellipse([x + r * 0.7, y - r * 0.35, x + r * 2.2, y + r * 0.8], fill=color)
    draw.ellipse([x + r * 1.6, y, x + r * 3.0, y + r], fill=color)
    draw.rounded_rectangle([x + r * 0.3, y + r * 0.35, x + r * 2.7, y + r * 1.1], radius=18, fill=color)


def draw_rabbit(draw, x, y, scale=1.0):
    color = (218, 170, 67, 230)
    draw.ellipse([x, y, x + 125 * scale, y + 105 * scale], fill=color)
    draw.ellipse([x + 30 * scale, y - 52 * scale, x + 88 * scale, y + 8 * scale], fill=color)
    draw.ellipse([x + 40 * scale, y - 112 * scale, x + 62 * scale, y - 30 * scale], fill=color)
    draw.ellipse([x + 70 * scale, y - 112 * scale, x + 92 * scale, y - 30 * scale], fill=color)


def draw_lanterns(draw):
    for x in [60, 920]:
        draw.line([x + 38, 60, x + 38, 110], fill=(255, 230, 170, 220), width=3)
        draw.ellipse([x, 110, x + 76, 220], fill=(220, 45, 38, 230), outline=(255, 216, 150, 230), width=3)
        draw.rectangle([x + 22, 214, x + 54, 230], fill=(255, 216, 150, 230))


def draw_christmas_tree(draw):
    x, y = 410, 390
    green = (18, 110, 82, 240)
    draw.polygon([(540, y), (350, y + 310), (730, y + 310)], fill=green)
    draw.polygon([(540, y + 170), (310, y + 520), (770, y + 520)], fill=green)
    draw.rectangle([510, y + 520, 570, y + 610], fill=(105, 68, 42, 230))


def draw_clock(draw):
    x, y, r = 540, 470, 170
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(255, 232, 180, 200), width=8)
    draw.line([x, y, x, y - 95], fill=(255, 232, 180, 220), width=6)
    draw.line([x, y, x + 70, y], fill=(255, 232, 180, 220), width=5)
    draw.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 232, 180, 255))


def draw_lotus(draw):
    color = (238, 218, 178, 220)
    x, y = 455, 525
    for petal in [[(x, y + 60), (x + 50, y - 10), (x + 100, y + 60)], [(x + 60, y + 55), (x + 110, y - 25), (x + 160, y + 55)], [(x + 120, y + 60), (x + 170, y - 10), (x + 220, y + 60)]]:
        draw.polygon(petal, fill=color)


def draw_mountain(draw):
    draw.polygon([(80, 760), (270, 420), (460, 760)], fill=(145, 135, 125, 105))
    draw.polygon([(370, 760), (590, 470), (820, 760)], fill=(150, 140, 130, 95))
    draw.polygon([(660, 760), (830, 520), (1010, 760)], fill=(160, 150, 138, 90))


def draw_text_card(draw, spec, box):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=34, fill=(255, 246, 226, 175), outline=(255, 230, 185, 180), width=2)

    title_font = get_font(74, bold=True)
    subtitle_font = get_font(34, bold=True)
    body_font = get_font(28)
    title_color = (92, 54, 20, 255)
    body_color = (118, 80, 45, 255)
    center_x = (x1 + x2) // 2
    y = y1 + 42

    def draw_centered(text, font, y_pos, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text((center_x - text_w // 2, y_pos), text, font=font, fill=fill)

    draw_centered(spec["title"], title_font, y, title_color)
    y += 90
    if spec.get("subtitle"):
        draw_centered(spec["subtitle"], subtitle_font, y, title_color)
        y += 52
    for line in wrap_text(spec.get("body", ""), 19)[:2]:
        draw_centered(line, body_font, y, body_color)
        y += 38


def render_poster(spec):
    random.seed(42)
    template = spec.get("template_key", "warm_gold")
    motifs = spec.get("motifs", [])
    density = spec.get("density", "medium")
    layout = spec.get("layout", "center_card")

    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))

    if template in ["hksar_formal_gold", "warm_gold"]:
        draw_gradient(img, "#E7B14F", "#C88A36")
        add_glow(img, (780, 250), 330, (255, 240, 190), 70)
    elif template in ["spring_red_gold", "national_red_grand"]:
        draw_gradient(img, "#C61E23", "#941018")
        add_glow(img, (760, 220), 360, (255, 220, 150), 85)
    elif template == "mid_autumn_gold":
        draw_gradient(img, "#DFA64A", "#BD7F2E")
        add_glow(img, (540, 470), 360, (255, 240, 190), 95)
    elif template == "christmas_red_green":
        draw_gradient(img, "#D83A32", "#A51218")
        add_glow(img, (520, 280), 320, (255, 245, 210), 55)
    elif template == "new_year_modern":
        draw_gradient(img, "#C82126", "#8F1118")
        add_glow(img, (540, 260), 380, (255, 235, 180), 70)
    elif template in ["ink_elegant", "ink_mountain"]:
        draw_gradient(img, "#F0E9DD", "#D8CDBF")
        add_glow(img, (780, 230), 280, (240, 205, 145), 65)
    else:
        draw_gradient(img, "#E0A547", "#C98C36")

    add_noise(img, 10)
    draw = ImageDraw.Draw(img)
    light_brand = template not in ["ink_elegant", "ink_mountain"]
    draw_brand(draw, 70, 55, light=light_brand)

    if "gold_rays" in motifs or density == "high":
        for r in [420, 500, 580]:
            draw.arc([540 - r, 220 - r, 540 + r, 220 + r], 8, 172, fill=(255, 230, 170, 45), width=2)
    if "skyline" in motifs:
        draw_skyline(draw, CANVAS_H - 300, color=(115, 32, 32, 150))
    if "fireworks" in motifs:
        draw_firework(draw, 265, 300, 70)
        draw_firework(draw, 820, 360, 82)
        if density == "high":
            draw_firework(draw, 730, 1010, 55)
            draw_firework(draw, 190, 1030, 50)
    if "bauhinia" in motifs:
        draw_bauhinia(draw, 540, 500, 1.45)
    if "moon" in motifs:
        draw_moon(draw, 540, 515, 210)
        draw_cloud(draw, 610, 575, 1.25)
    if "rabbit" in motifs:
        draw_rabbit(draw, 465, 680, 1.05)
    if "clouds" in motifs and "moon" not in motifs:
        draw_cloud(draw, 130, 390, 1.05)
        draw_cloud(draw, 660, 690, 1.15)
    if "lanterns" in motifs:
        draw_lanterns(draw)
    if "tree" in motifs:
        draw_christmas_tree(draw)
    if "clock" in motifs:
        draw_clock(draw)
    if "lotus" in motifs:
        draw_lotus(draw)
    if "mountain" in motifs:
        draw_mountain(draw)
    if "snowflakes" in motifs:
        for x, y in [(170, 320), (860, 280), (780, 760), (260, 870)]:
            draw_firework(draw, x, y, 28, color=(255, 255, 255, 180))
    if "gold_particles" in motifs:
        count = 90 if density == "high" else 45
        for _ in range(count):
            x = random.randint(80, CANVAS_W - 80)
            y = random.randint(210, CANVAS_H - 260)
            r = random.randint(1, 3)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 232, 165, random.randint(70, 170)))

    if layout == "top_title":
        card_box = [120, 190, 960, 485]
    elif layout == "left_editorial":
        card_box = [85, 390, 640, 760]
    elif layout == "lower_card":
        card_box = [120, 755, 960, 1060]
    else:
        card_box = [130, 455, 950, 755]
    draw_text_card(draw, spec, card_box)

    draw.pieslice([-150, CANVAS_H - 260, CANVAS_W + 150, CANVAS_H + 180], 180, 360, fill=(255, 255, 255, 245))
    draw_brand(draw, 70, CANVAS_H - 145, light=False)

    if spec.get("qr_reserved", True):
        x1, y1 = CANVAS_W - 210, CANVAS_H - 185
        draw.rounded_rectangle([x1, y1, x1 + 140, y1 + 140], radius=14, fill=(255, 255, 255, 245), outline=(210, 210, 210, 255), width=3)
        draw.text((x1 + 43, y1 + 54), "QR", font=get_font(28, bold=True), fill=(120, 120, 120, 255))
    return img


def pil_to_bytes(img):
    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()


def build_base_spec(holiday_key, template_key, layout, density, qr_reserved):
    holiday = HOLIDAYS[holiday_key]
    return {
        "holiday_key": holiday_key,
        "holiday_name": holiday["name"],
        "title": holiday["title"],
        "subtitle": holiday["subtitle"],
        "body": holiday["body"],
        "template_key": holiday["template"] if template_key == "auto" else template_key,
        "layout": "center_card" if layout == "auto" else layout,
        "density": "medium" if density == "auto" else density,
        "motifs": holiday["motifs"],
        "qr_reserved": qr_reserved,
    }


def generate_spec(base_spec, instruction, use_llm, provider_name, model_override, debug):
    base_spec = rule_adjust_spec(base_spec, instruction)
    if not use_llm:
        return base_spec, None
    system_prompt, user_prompt = build_prompt(base_spec, instruction)
    try:
        result = call_llm(provider_name, model_override, system_prompt, user_prompt, debug=debug)
        parsed = extract_json(result["content"])
        final_spec = clean_spec(parsed, base_spec)
        final_spec = rule_adjust_spec(final_spec, instruction)
        return final_spec, {"success": True, "provider": result["provider"], "model": result["model"], "raw": result["content"]}
    except Exception as e:
        return base_spec, {"success": False, "error": str(e)}


st.title("🎨 GF Securities Poster Agent")
st.caption("Template-based poster generator. LLM writes copy and selects design spec; renderer produces stable company-style output.")

with st.sidebar:
    st.header("Poster Settings")
    holiday_key = st.selectbox(
        "節日主題 / Holiday Theme",
        options=list(HOLIDAYS.keys()),
        format_func=lambda x: HOLIDAYS[x]["name"],
        index=list(HOLIDAYS.keys()).index("hksar_day"),
    )
    template_key = st.selectbox("模板 / Template", options=list(TEMPLATES.keys()), format_func=lambda x: TEMPLATES[x], index=0)
    layout = st.selectbox("版式 / Layout", options=list(LAYOUTS.keys()), format_func=lambda x: LAYOUTS[x], index=0)
    density = st.selectbox(
        "元素密度 / Density",
        options=["auto", "low", "medium", "high"],
        format_func=lambda x: "Auto / 自動" if x == "auto" else DENSITIES[x],
        index=0,
    )
    qr_reserved = st.checkbox("Reserve QR area / 預留二維碼位置", value=True)

    st.divider()
    st.header("AI Provider")
    use_llm = st.toggle("Use LLM for copy & design spec", value=True)
    providers = available_providers()
    if providers:
        provider_name = st.selectbox("Provider", options=providers, index=0)
        st.success(f"Configured: {provider_name}")
    else:
        provider_name = "OPENROUTER"
        st.warning("No valid provider detected. Check Secrets.")
    model_override = st.text_input("Model override（可留空）", value="", placeholder="Leave empty to use model from Secrets/default")
    debug = st.checkbox("Show LLM debug", value=False)

    if st.button("Test LLM Connection", use_container_width=True):
        if not providers:
            st.error("No provider configured.")
        else:
            try:
                response = call_llm(
                    provider_name=provider_name,
                    model_override=model_override,
                    system_prompt="Reply with valid JSON only.",
                    user_prompt='{"status":"ok","message":"API connection works"}',
                    debug=True,
                )
                st.success("LLM connection works.")
                with st.expander("Raw response"):
                    st.write(response["content"])
            except Exception as e:
                st.error(str(e))

st.divider()
st.subheader("1. Generate Poster")
instruction = st.text_area(
    "輸入文案和版式要求 / Copywriting & layout instruction",
    value="面向客戶，背景增加香港元素，字體放畫面中間，語氣官方一些。",
    height=120,
)

if st.button("Generate Poster"):
    base_spec = build_base_spec(holiday_key, template_key, layout, density, qr_reserved)
    spec, llm_info = generate_spec(
        base_spec=base_spec,
        instruction=instruction,
        use_llm=use_llm and bool(providers),
        provider_name=provider_name,
        model_override=model_override,
        debug=debug,
    )
    poster = render_poster(spec)
    poster_bytes = pil_to_bytes(poster)
    st.session_state["poster_spec"] = spec
    st.session_state["poster_bytes"] = poster_bytes
    st.session_state["llm_info"] = llm_info

    if llm_info and llm_info.get("success"):
        st.success(f"Poster generated with LLM: {llm_info.get('provider')} / {llm_info.get('model')}")
    elif llm_info and not llm_info.get("success"):
        st.warning(f"Poster generated with fallback rules. LLM error: {llm_info.get('error')}")
    else:
        st.success("Poster generated.")

if "poster_bytes" in st.session_state:
    col1, col2 = st.columns([1.3, 1], gap="large")
    with col1:
        st.image(st.session_state["poster_bytes"], use_container_width=True)
        st.download_button(
            "Download PNG",
            data=st.session_state["poster_bytes"],
            file_name="gf_festival_poster.png",
            mime="image/png",
            use_container_width=True,
        )
    with col2:
        spec = st.session_state["poster_spec"]
        st.subheader("Generation Summary")
        st.write(f"**Holiday:** {spec['holiday_name']}")
        st.write(f"**Template:** {TEMPLATES.get(spec['template_key'], spec['template_key'])}")
        st.write(f"**Layout:** {LAYOUTS.get(spec['layout'], spec['layout'])}")
        st.write(f"**Density:** {DENSITIES.get(spec['density'], spec['density'])}")
        st.write(f"**Motifs:** {', '.join(spec.get('motifs', []))}")
        with st.expander("Debug JSON"):
            st.json(spec)
        if debug and st.session_state.get("llm_info"):
            with st.expander("LLM Debug"):
                st.json(st.session_state["llm_info"])
else:
    st.info("Select settings and click Generate Poster.")

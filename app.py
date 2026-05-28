import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import random
import math


# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="GF Poster Agent",
    page_icon="🎨",
    layout="wide"
)


# ---------------------------------------------------
# Poster type / style library
# ---------------------------------------------------
POSTER_TYPES = {
    "closure_notice": "假期休市通知 / Holiday Market Closure Notice",
    "festival_greeting": "节日祝福海报 / Festival Greeting Poster"
}

STYLE_LIBRARY = {
    "closure_ink": {
        "style_name": "水墨节气休市通知",
        "poster_type": "closure_notice",
        "background": "#F4F0E8",
        "accent": "#D99A4E",
        "text": "#222222",
        "card": "#FFFFFF",
        "tone": "traditional, elegant, formal, client-facing",
        "elements": ["ink_mountain", "sun", "calendar_card"]
    },
    "closure_red": {
        "style_name": "红金节庆休市通知",
        "poster_type": "closure_notice",
        "background": "#B71919",
        "accent": "#D99A4E",
        "text": "#222222",
        "card": "#FFF8F0",
        "tone": "festive, clear, client-facing",
        "elements": ["lantern", "gold_cloud", "calendar_card"]
    },
    "greeting_red_gold": {
        "style_name": "红金节日祝福",
        "poster_type": "festival_greeting",
        "background": "#B70F0F",
        "accent": "#F2C16B",
        "text": "#FFF4D6",
        "card": "#FFFFFF",
        "tone": "festive, warm, corporate",
        "elements": ["firework", "lantern", "gold_curve"]
    },
    "greeting_warm_gold": {
        "style_name": "暖金中秋祝福",
        "poster_type": "festival_greeting",
        "background": "#D99A3D",
        "accent": "#FFF2C6",
        "text": "#7A4A12",
        "card": "#FFFFFF",
        "tone": "warm, elegant, poetic, client-facing",
        "elements": ["moon", "cloud", "branch"]
    },
    "greeting_modern_red": {
        "style_name": "现代红色品牌祝福",
        "poster_type": "festival_greeting",
        "background": "#C91616",
        "accent": "#FFD68A",
        "text": "#FFF4E0",
        "card": "#FFFFFF",
        "tone": "modern, bold, branded",
        "elements": ["geometry", "firework", "brand_symbol"]
    }
}


# ---------------------------------------------------
# Fonts
# ---------------------------------------------------
def load_font(size, bold=False):
    """
    Load CJK-compatible font if available.
    For Streamlit Cloud, add packages.txt with: fonts-noto-cjk
    """
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    return ImageFont.load_default()


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def image_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def draw_centered_text(draw, text, y, font, fill, width=900):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (width - text_w) // 2
    draw.text((x, y), text, fill=fill, font=font)


def draw_wrapped_text(draw, text, x, y, font, fill, max_width, line_gap=12):
    """
    Better wrapping for Chinese and English mixed text.
    """
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


def add_noise_texture(img, opacity=18):
    """
    Add subtle paper texture.
    """
    w, h = img.size
    noise = Image.new("L", (w, h))
    pixels = noise.load()

    for i in range(w):
        for j in range(h):
            pixels[i, j] = random.randint(220, 255)

    noise = noise.convert("RGB")
    img = Image.blend(img, noise, opacity / 255)
    return img


# ---------------------------------------------------
# Preset content generation
# ---------------------------------------------------
def generate_poster_state(user_prompt, poster_type, style_key):
    prompt = user_prompt.lower()
    style = STYLE_LIBRARY[style_key]

    if poster_type == "closure_notice":
        # Default: Chung Yeung Festival
        state = {
            "poster_type": "closure_notice",
            "style_key": style_key,
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
        }

        if "thanksgiving" in prompt or "感恩" in prompt:
            state.update({
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
            })

        if "spring" in prompt or "春節" in prompt or "春节" in prompt or "new year" in prompt:
            state.update({
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
            })

        return state

    # Festival greeting
    state = {
        "poster_type": "festival_greeting",
        "style_key": style_key,
        "title": "節日快樂",
        "subtitle": "廣發證券（香港）祝您節日愉快",
        "blessing": "願您與家人平安喜樂，萬事順遂。",
        "holiday": "festival"
    }

    if "mid-autumn" in prompt or "中秋" in prompt or "moon" in prompt:
        state.update({
            "title": "情滿中秋\n月圓人團圓",
            "subtitle": "廣發證券（香港）祝您中秋快樂",
            "blessing": "月滿人團圓，佳節共安康。",
            "holiday": "mid_autumn"
        })

    elif "christmas" in prompt or "聖誕" in prompt or "圣诞" in prompt:
        state.update({
            "title": "MERRY\nCHRISTMAS",
            "subtitle": "聖誕快樂",
            "blessing": "願節日的溫暖與喜悅常伴您左右。",
            "holiday": "christmas"
        })

    elif "spring" in prompt or "春節" in prompt or "春节" in prompt or "new year" in prompt or "新春" in prompt:
        state.update({
            "title": "恭賀新春",
            "subtitle": "廣發證券（香港）祝您新春快樂",
            "blessing": "馬到功成，財源廣進。",
            "holiday": "spring_festival"
        })

    elif "元旦" in prompt or "new year" in prompt:
        state.update({
            "title": "元旦新禧",
            "subtitle": "HAPPY NEW YEAR",
            "blessing": "年首初月，歲如熹光。",
            "holiday": "new_year"
        })

    return state


# ---------------------------------------------------
# Background / decorations
# ---------------------------------------------------
def draw_company_brand(draw, x, y, color="#B8A06A", scale=1.0):
    logo_font = load_font(int(42 * scale), bold=True)
    sub_font = load_font(int(18 * scale), bold=False)

    # Simple GF-like symbol placeholder
    draw.rounded_rectangle(
        [x, y + 8, x + int(70 * scale), y + int(48 * scale)],
        radius=int(16 * scale),
        outline=color,
        width=int(5 * scale)
    )
    draw.text((x + int(88 * scale), y), "廣發證券（香港）", fill=color, font=logo_font)
    draw.text(
        (x + int(90 * scale), y + int(50 * scale)),
        "GF SECURITIES (HONG KONG)",
        fill=color,
        font=sub_font
    )


def draw_ink_mountain_scene(draw, width, height, style):
    # sun
    draw.ellipse([610, 220, 790, 400], fill="#E7A15F")

    # mountains
    mountain_color = "#D8D8D8"
    draw.polygon([(0, 430), (130, 330), (250, 440)], fill=mountain_color)
    draw.polygon([(620, 520), (760, 410), (930, 520)], fill="#D0D0D0")
    draw.polygon([(360, 500), (520, 410), (690, 510)], fill="#E1E1E1")

    # birds
    bird_font = load_font(26)
    for bx, by in [(160, 280), (690, 430), (720, 450), (760, 440)]:
        draw.text((bx, by), "⌁", fill="#888888", font=bird_font)

    # grass lines
    for i in range(6):
        x = 40 + i * 20
        draw.arc([x, 520 - i * 8, x + 180, 760], 210, 285, fill="#C8B27D", width=2)


def draw_lantern(draw, x, y, scale=1.0):
    red = "#D7261E"
    gold = "#F4C46A"
    w = int(70 * scale)
    h = int(110 * scale)
    draw.ellipse([x, y, x + w, y + h], fill=red, outline=gold, width=3)
    draw.line([x + w // 2, y - 30, x + w // 2, y], fill=gold, width=3)
    draw.rectangle([x + 20, y + h - 5, x + w - 20, y + h + 10], fill=gold)
    draw.line([x + w // 2, y + h + 10, x + w // 2, y + h + 45], fill=gold, width=2)


def draw_firework(draw, cx, cy, r, color="#FFD68A"):
    for i in range(18):
        angle = 2 * math.pi * i / 18
        x1 = cx + int(math.cos(angle) * r * 0.35)
        y1 = cy + int(math.sin(angle) * r * 0.35)
        x2 = cx + int(math.cos(angle) * r)
        y2 = cy + int(math.sin(angle) * r)
        draw.line([x1, y1, x2, y2], fill=color, width=3)


# ---------------------------------------------------
# Closure notice renderer
# ---------------------------------------------------
def render_closure_notice(state):
    width, height = 900, 1600
    style = STYLE_LIBRARY[state["style_key"]]
    bg = style["background"]
    accent = style["accent"]

    img = Image.new("RGB", (width, height), bg)
    img = add_noise_texture(img, opacity=16)
    draw = ImageDraw.Draw(img)

    title_font = load_font(92, bold=True)
    subtitle_font = load_font(32)
    small_font = load_font(26)
    medium_font = load_font(34)
    body_font = load_font(38)
    detail_font = load_font(34)

    if state["style_key"] == "closure_ink":
        draw_ink_mountain_scene(draw, width, height, style)
        title_color = "#111111"
        subtitle_color = "#333333"
    else:
        # Red festive top
        draw.rectangle([0, 0, width, 600], fill="#B71919")
        draw_lantern(draw, 40, 60, 0.9)
        draw_lantern(draw, width - 110, 60, 0.9)
        draw_firework(draw, 220, 250, 60, "#FFD68A")
        draw_firework(draw, 720, 280, 70, "#FFD68A")
        title_color = "#FFF0C2"
        subtitle_color = "#FFF8E8"

    # Title area
    draw_centered_text(draw, state["title"], 120, title_font, title_color, width)
    draw_centered_text(draw, state["subtitle"], 250, subtitle_font, subtitle_color, width)

    # Festival label
    label_w, label_h = 210, 46
    label_x = (width - label_w) // 2
    draw.rounded_rectangle(
        [label_x, 330, label_x + label_w, 330 + label_h],
        radius=22,
        outline="#B8A06A",
        width=2,
        fill="#F7EFE3" if state["style_key"] == "closure_ink" else "#FFF3D3"
    )
    draw_centered_text(draw, state["festival_label"], 338, small_font, "#9A7A3D", width)

    # Calendar card
    card_x1, card_y1 = 45, 590
    card_x2, card_y2 = width - 45, 1470
    draw.rounded_rectangle(
        [card_x1, card_y1, card_x2, card_y2],
        radius=34,
        fill=style["card"],
        outline="#E7E2D8",
        width=2
    )

    # Hanging pins
    pin_color = "#C8A36A"
    draw.rounded_rectangle([135, 560, 155, 640], radius=10, fill=pin_color)
    draw.rounded_rectangle([width - 155, 560, width - 135, 640], radius=10, fill=pin_color)

    # Year
    draw_centered_text(draw, f"- {state['year']} -", card_y1 + 55, load_font(52, bold=True), "#222222", width)

    # Month label
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
        detail_y += 25

    # Company brand
    draw_company_brand(draw, 165, height - 115, color="#B8A06A", scale=0.78)

    return img


# ---------------------------------------------------
# Festival greeting renderer
# ---------------------------------------------------
def render_festival_greeting(state):
    width, height = 900, 1600
    style = STYLE_LIBRARY[state["style_key"]]
    bg = style["background"]
    accent = style["accent"]
    text_color = style["text"]

    img = Image.new("RGB", (width, height), bg)
    img = add_noise_texture(img, opacity=8)
    draw = ImageDraw.Draw(img)

    title_font = load_font(76, bold=True)
    big_font = load_font(92, bold=True)
    subtitle_font = load_font(36)
    body_font = load_font(34)

    # Background motifs
    if state["style_key"] == "greeting_warm_gold":
        # Warm Mid-Autumn style
        draw.ellipse([150, 380, 750, 980], fill="#FFF4C8")
        draw.ellipse([190, 420, 710, 940], fill="#FBE7A5")
        draw.arc([110, 340, 790, 1020], 20, 340, fill="#F6D98B", width=3)

        # branch
        for i in range(5):
            draw.line([60, 410 + i * 30, 300, 320 + i * 20], fill="#8A5A20", width=4)

        # clouds
        draw.ellipse([430, 650, 620, 720], fill="#FFF9D8")
        draw.ellipse([540, 625, 720, 705], fill="#FFF9D8")

    elif state["style_key"] == "greeting_modern_red":
        # Modern geometry
        draw.polygon([(0, 300), (900, 160), (900, 520), (0, 620)], fill="#E85A3C")
        draw.polygon([(210, 360), (560, 260), (350, 1220), (0, 1220)], fill="#A80F0F")
        draw.ellipse([520, 660, 950, 1090], fill="#E46B3E")
        draw.ellipse([610, 750, 850, 990], fill="#C91616")
        draw_firework(draw, 210, 1050, 90, "#FFF1C4")
        draw_firework(draw, 710, 680, 70, "#FFF1C4")

    else:
        # Red gold festive
        draw_lantern(draw, 35, 80, 1.0)
        draw_lantern(draw, width - 105, 80, 1.0)
        draw_firework(draw, 220, 360, 80, "#FFD68A")
        draw_firework(draw, 710, 430, 90, "#FFD68A")
        draw.ellipse([400, 510, 980, 1090], fill="#D4442A")

    # Company brand at top
    draw_company_brand(draw, 70, 70, color="#E4D0A1", scale=0.7)

    # Main title
    title_lines = state["title"].split("\n")
    title_y = 260

    for line in title_lines:
        font = big_font if len(line) <= 6 else title_font
        draw_centered_text(draw, line, title_y, font, text_color, width)
        title_y += font.size + 18

    # Subtitle and blessing
    draw_centered_text(draw, state["subtitle"], title_y + 40, subtitle_font, text_color, width)
    draw_centered_text(draw, state["blessing"], title_y + 105, body_font, text_color, width)

    # Holiday elements
    if state["holiday"] == "christmas":
        # Simple tree
        tree_x, tree_y = width // 2, 620
        green = "#0C6B4E"
        draw.polygon([(tree_x, tree_y), (tree_x - 170, tree_y + 260), (tree_x + 170, tree_y + 260)], fill=green)
        draw.polygon([(tree_x, tree_y + 160), (tree_x - 210, tree_y + 450), (tree_x + 210, tree_y + 450)], fill=green)
        draw.rectangle([tree_x - 35, tree_y + 450, tree_x + 35, tree_y + 560], fill="#0C6B4E")
        draw_firework(draw, tree_x, tree_y - 20, 35, "#FFD68A")

    elif state["holiday"] == "spring_festival":
        # Red packet / horse-like card
        draw.rounded_rectangle([270, 590, 630, 940], radius=30, fill="#FCE6B0")
        draw.rounded_rectangle([310, 640, 590, 900], radius=20, fill="#D92020")
        draw.ellipse([390, 705, 520, 835], fill="#F7B15A")
        draw.text((360, 1010), "恭 賀 新 春", fill=text_color, font=load_font(60, bold=True))

    elif state["holiday"] == "mid_autumn":
        # Moon rabbit
        draw.ellipse([360, 740, 540, 900], fill="#DFAE45")
        draw.ellipse([440, 700, 490, 780], fill="#DFAE45")
        draw.ellipse([385, 700, 435, 780], fill="#DFAE45")

    elif state["holiday"] == "new_year":
        draw.line([450, 340, 450, 740], fill="#FFF6DA", width=12)
        draw.ellipse([405, 240, 495, 330], fill="#FFF6DA")
        draw_firework(draw, 220, 980, 80, "#FFF6DA")
        draw_firework(draw, 700, 1030, 80, "#FFF6DA")

    # Bottom white wave / QR reserved area
    draw.pieslice([-160, height - 350, width + 160, height + 220], 180, 360, fill="#FFFFFF")
    draw_company_brand(draw, 70, height - 150, color="#B8A06A", scale=0.75)

    # QR placeholder
    draw.rounded_rectangle(
        [700, height - 170, 820, height - 50],
        radius=12,
        outline="#D8D8D8",
        width=3
    )
    draw.text((705, height - 25), "QR reserved", fill="#999999", font=load_font(18))

    return img


# ---------------------------------------------------
# Main renderer
# ---------------------------------------------------
def generate_poster(state):
    if state["poster_type"] == "closure_notice":
        return render_closure_notice(state)
    return render_festival_greeting(state)


# ---------------------------------------------------
# Simple revision
# ---------------------------------------------------
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
        if updated["poster_type"] == "closure_notice":
            updated["style_key"] = "closure_red"
        else:
            updated["style_key"] = "greeting_red_gold"

    if "金色" in revision or "gold" in r:
        if updated["poster_type"] == "festival_greeting":
            updated["style_key"] = "greeting_warm_gold"

    return updated


# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.title("🎨 GF Securities Poster Agent")
st.write("Generate holiday market closure notices and festival greeting posters based on company-style templates.")

with st.sidebar:
    st.header("Poster Settings")

    poster_type = st.selectbox(
        "海报类型 / Poster Type",
        options=list(POSTER_TYPES.keys()),
        format_func=lambda x: POSTER_TYPES[x]
    )

    available_styles = [
        key for key, value in STYLE_LIBRARY.items()
        if value["poster_type"] == poster_type
    ]

    style_key = st.selectbox(
        "参考风格 / Reference Style",
        options=available_styles,
        format_func=lambda x: STYLE_LIBRARY[x]["style_name"]
    )

    st.caption("Current style profile")
    st.json(STYLE_LIBRARY[style_key])

st.divider()

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
        state = generate_poster_state(user_prompt, poster_type, style_key)
        state["style_key"] = style_key

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

st.subheader("2. Revise Poster")

revision_prompt = st.text_area(
    "输入修改指令 / Revision instruction",
    placeholder="例如：语气更正式一点 / 改成红金风格 / 文案更简短 / 更温暖一点",
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

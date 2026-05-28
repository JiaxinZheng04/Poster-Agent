import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import re


# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Poster Agent",
    page_icon="🎨",
    layout="wide"
)


# ---------------------------------------------------
# Style library
# ---------------------------------------------------
STYLE_LIBRARY = {
    "formal_notice": {
        "style_name": "Formal Notice",
        "primary_colors": ["#102A43", "#D4AF37", "#F8FAFC"],
        "tone": "formal, professional, client-facing",
        "layout": "top header with large content card",
        "decorative_elements": ["minimal lines", "small icons"],
        "text_density": "medium"
    },
    "festival_greeting": {
        "style_name": "Festival Greeting",
        "primary_colors": ["#0F1B2D", "#F6D365", "#FFF7E6"],
        "tone": "warm, elegant, festive, client-facing",
        "layout": "dark background with elegant light card",
        "decorative_elements": ["moon", "stars", "gold accent"],
        "text_density": "low"
    },
    "promotion_modern": {
        "style_name": "Promotion Modern",
        "primary_colors": ["#FFF7ED", "#EA580C", "#1F2937"],
        "tone": "clear, energetic, marketing-oriented",
        "layout": "bold title with product highlight card",
        "decorative_elements": ["rounded shapes", "highlight badges"],
        "text_density": "medium"
    }
}


# ---------------------------------------------------
# Font loading
# ---------------------------------------------------
def load_font(size, bold=False):
    """
    Load a safe system font for Streamlit Cloud.
    """
    try:
        if bold:
            return ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
            )
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
        )
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------
# Utility helpers
# ---------------------------------------------------
def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def image_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def get_style_profile(style_key):
    return STYLE_LIBRARY.get(style_key, STYLE_LIBRARY["formal_notice"])


def get_render_palette(style_profile):
    """
    Convert style profile colors into render colors.
    """
    colors = style_profile["primary_colors"]

    # Expect 3 colors:
    # 0 -> background / primary
    # 1 -> accent
    # 2 -> light card or dark text color
    background = colors[0]
    accent = colors[1]
    third = colors[2]

    # Decide text/card based on background darkness
    if background.lower() in ["#102a43", "#0f1b2d", "#1f2937", "#1f1b18"]:
        header_text = "#FFFFFF"
        subtitle_text = "#F5F5F5"
        card_fill = third if third.startswith("#") else "#FFFFFF"
        body_text = "#1F2933"
    else:
        header_text = "#1F2933"
        subtitle_text = "#374151"
        card_fill = "#FFFFFF"
        body_text = "#1F2933"

    return {
        "background": background,
        "accent": accent,
        "card_fill": card_fill,
        "header_text": header_text,
        "subtitle_text": subtitle_text,
        "body_text": body_text
    }


# ---------------------------------------------------
# Prompt parsing
# Rule-based for now (stable MVP)
# ---------------------------------------------------
def generate_poster_state(user_prompt, style_key):
    prompt = user_prompt.strip()
    prompt_lower = prompt.lower()
    style_profile = get_style_profile(style_key)

    # Default based on style
    state = {
        "style_key": style_key,
        "title": "Poster Draft",
        "subtitle": style_profile["style_name"],
        "body": [
            "This is a simple poster draft generated from your instruction.",
            "You can refine the message and style using the revision box below."
        ],
        "cta": "Learn More",
        "theme": style_key
    }

    # Festival / Mid-Autumn
    if "mid-autumn" in prompt_lower or "mid autumn" in prompt_lower or "moon festival" in prompt_lower:
        state = {
            "style_key": style_key,
            "title": "Mid-Autumn Festival",
            "subtitle": "Moonlight, reunion, and warm wishes",
            "body": [
                "Celebrate the beauty of the full moon with warmth and joy.",
                "Share mooncakes, stories, and meaningful moments with family and friends.",
                "Wishing you peace, happiness, and togetherness this festive season."
            ],
            "cta": "Happy Mid-Autumn Festival",
            "theme": "festival_greeting"
        }

    # Coffee / Cafe
    elif "coffee" in prompt_lower or "latte" in prompt_lower or "cafe" in prompt_lower:
        state = {
            "style_key": style_key,
            "title": "Fresh Coffee Moments",
            "subtitle": "A warm cup for a better day",
            "body": [
                "Enjoy smooth, freshly brewed coffee made for your daily pause.",
                "Rich aroma, balanced taste, and a comforting finish.",
                "Perfect for mornings, meetings, and quiet afternoons."
            ],
            "cta": "Try It Today",
            "theme": "promotion_modern"
        }

    # Market closure / notice
    elif "market closure" in prompt_lower or "closure notice" in prompt_lower or "holiday notice" in prompt_lower or "notice" in prompt_lower:
        state = {
            "style_key": style_key,
            "title": "Market Closure Notice",
            "subtitle": "Important update for clients",
            "body": [
                "Please note the market closure arrangement during the holiday period.",
                "Kindly make trading and settlement plans in advance.",
                "Normal operations will resume according to the official schedule."
            ],
            "cta": "Please Plan Ahead",
            "theme": "formal_notice"
        }

    # Recruitment / career
    elif "recruitment" in prompt_lower or "career" in prompt_lower or "job" in prompt_lower or "hiring" in prompt_lower:
        state = {
            "style_key": style_key,
            "title": "Career Opportunity",
            "subtitle": "Build your future with us",
            "body": [
                "We are looking for motivated and talented individuals to join our team.",
                "Grow your skills, expand your experience, and make a real impact.",
                "Apply now and take the next step in your career journey."
            ],
            "cta": "Apply Now",
            "theme": "promotion_modern"
        }

    # Promotion / campaign / product
    elif "promotion" in prompt_lower or "campaign" in prompt_lower or "product" in prompt_lower or "sale" in prompt_lower:
        state = {
            "style_key": style_key,
            "title": "Special Promotion",
            "subtitle": "Fresh offers designed for you",
            "body": [
                "Discover exciting highlights and limited-time offers.",
                "Clear message, strong value, and modern visual presentation.",
                "A simple promotional poster designed for impact."
            ],
            "cta": "Explore Now",
            "theme": "promotion_modern"
        }

    # If user prompt is very short but style is festival
    elif style_key == "festival_greeting":
        state = {
            "style_key": style_key,
            "title": "Festival Greeting",
            "subtitle": "Warm wishes for the season",
            "body": [
                "A thoughtful festive greeting poster for clients and partners.",
                "Elegant, warm, and suitable for professional holiday communication."
            ],
            "cta": "Best Wishes",
            "theme": "festival_greeting"
        }

    elif style_key == "formal_notice":
        state = {
            "style_key": style_key,
            "title": "Important Notice",
            "subtitle": "Please review the latest update",
            "body": [
                "This poster follows a formal and client-facing communication style.",
                "Suitable for announcements, notices, and service arrangements."
            ],
            "cta": "Read More",
            "theme": "formal_notice"
        }

    elif style_key == "promotion_modern":
        state = {
            "style_key": style_key,
            "title": "New Highlights",
            "subtitle": "Clear, modern, and visually engaging",
            "body": [
                "This poster is designed for campaigns, products, or promotional announcements.",
                "The tone is more energetic and marketing-oriented."
            ],
            "cta": "Check It Out",
            "theme": "promotion_modern"
        }

    return state


# ---------------------------------------------------
# Revision logic
# Simple rule-based revision for MVP
# ---------------------------------------------------
def revise_poster_state(current_state, revision_prompt):
    updated = current_state.copy()
    revision = revision_prompt.strip().lower()

    # More formal
    if "formal" in revision or "professional" in revision:
        updated["subtitle"] = "A more formal and client-facing version"
        updated["cta"] = "Please Take Note"

    # More elegant
    if "elegant" in revision or "premium" in revision:
        updated["subtitle"] = "A more elegant and refined visual style"

    # More warm
    if "warm" in revision or "friendly" in revision:
        updated["subtitle"] = "A warmer and more welcoming message"

    # Simpler text
    if "simple" in revision or "minimal" in revision or "shorter" in revision:
        updated["body"] = [
            "A cleaner and more concise poster message.",
            "Focused on the key idea with a simple visual style."
        ]

    # Change title
    if "title" in revision and "change" in revision:
        updated["title"] = "Updated Poster Title"

    # Mid-Autumn reunion angle
    if "reunion" in revision:
        updated["title"] = "A Season of Reunion"
        updated["subtitle"] = "Under the same moon, we gather in warmth"

    # Client-facing
    if "client" in revision:
        updated["body"] = [
            "This version is adjusted for a more client-facing tone.",
            "Clear, respectful, and suitable for professional communication."
        ]
        updated["cta"] = "With Best Regards"

    return updated


# ---------------------------------------------------
# Drawing decorative elements
# ---------------------------------------------------
def draw_decorations(draw, width, height, theme, style_profile, colors):
    elements = style_profile.get("decorative_elements", [])

    if theme == "festival_greeting" or "moon" in elements:
        # Moon
        draw.ellipse([780, 90, 980, 290], fill="#F9E7A1")
        draw.ellipse([730, 80, 930, 280], fill=colors["background"])

        # Stars
        for x, y in [(150, 130), (240, 220), (920, 390), (840, 470), (170, 450)]:
            draw.ellipse([x, y, x + 8, y + 8], fill=colors["accent"])

    elif theme == "formal_notice":
        # Minimal line chart / notice accent
        draw.line([760, 250, 830, 190, 900, 225, 980, 140], fill=colors["accent"], width=7)
        draw.ellipse([753, 243, 767, 257], fill=colors["accent"])
        draw.ellipse([823, 183, 837, 197], fill=colors["accent"])
        draw.ellipse([893, 218, 907, 232], fill=colors["accent"])
        draw.ellipse([973, 133, 987, 147], fill=colors["accent"])

    elif theme == "promotion_modern":
        # Modern circles / badge shapes
        draw.ellipse([810, 100, 980, 270], outline=colors["accent"], width=8)
        draw.ellipse([850, 140, 940, 230], outline=colors["accent"], width=4)
        draw.rounded_rectangle([810, 300, 980, 360], radius=20, fill=colors["accent"])


# ---------------------------------------------------
# Poster rendering
# ---------------------------------------------------
def generate_poster(poster_state):
    width, height = 1080, 1350
    style_profile = get_style_profile(poster_state["style_key"])
    colors = get_render_palette(style_profile)

    img = Image.new("RGB", (width, height), color=colors["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(70, bold=True)
    subtitle_font = load_font(32)
    body_font = load_font(34)
    cta_font = load_font(40, bold=True)
    footer_font = load_font(22)

    # Decorations
    draw_decorations(draw, width, height, poster_state["theme"], style_profile, colors)

    # Header
    draw.text((80, 120), poster_state["title"], fill=colors["accent"] if colors["background"].lower() in ["#0f1b2d", "#102a43"] else colors["header_text"], font=title_font)
    draw.text((84, 220), poster_state["subtitle"], fill=colors["subtitle_text"], font=subtitle_font)

    # Content card
    card_x1, card_y1 = 80, 390
    card_x2, card_y2 = width - 80, height - 180

    draw.rounded_rectangle(
        [card_x1, card_y1, card_x2, card_y2],
        radius=38,
        fill=colors["card_fill"]
    )

    # Body text
    y = card_y1 + 90
    for paragraph in poster_state["body"]:
        wrapped_lines = textwrap.wrap(paragraph, width=40)
        for line in wrapped_lines:
            draw.text((card_x1 + 70, y), line, fill=colors["body_text"], font=body_font)
            y += 50
        y += 28

    # CTA block
    draw.rounded_rectangle(
        [card_x1 + 70, card_y2 - 170, card_x2 - 70, card_y2 - 70],
        radius=26,
        fill=colors["accent"]
    )
    draw.text(
        (card_x1 + 100, card_y2 - 143),
        poster_state["cta"],
        fill="#FFFFFF",
        font=cta_font
    )

    # Footer
    draw.text(
        (80, height - 90),
        f"Poster Agent · {style_profile['style_name']}",
        fill="#FFFFFF" if colors["background"].lower() in ["#102a43", "#0f1b2d", "#1f2937"] else "#374151",
        font=footer_font
    )

    return img


# ---------------------------------------------------
# Streamlit UI
# ---------------------------------------------------
st.title("🎨 Poster Agent")
st.write("Generate simple posters with a chosen reference style.")

with st.sidebar:
    st.header("Reference Style")

    style_choice = st.selectbox(
        "Choose a reference style",
        options=["formal_notice", "festival_greeting", "promotion_modern"],
        format_func=lambda x: STYLE_LIBRARY[x]["style_name"]
    )

    selected_style = STYLE_LIBRARY[style_choice]

    st.caption("Current style profile")
    st.json(selected_style)

st.divider()

# -------------------------
# Create poster
# -------------------------
st.subheader("1. Create a Poster")

user_prompt = st.text_area(
    "Enter your poster instruction:",
    placeholder="Example: Create a simple Mid-Autumn Festival poster for clients.",
    height=130
)

if st.button("Generate Poster"):
    if user_prompt.strip() == "":
        st.warning("Please enter a poster instruction first.")
    else:
        poster_state = generate_poster_state(user_prompt, style_choice)
        st.session_state["poster_state"] = poster_state
        st.session_state["style_choice"] = style_choice

        poster = generate_poster(poster_state)
        st.session_state["poster"] = poster

        st.success("Poster generated!")

        col1, col2 = st.columns([1.3, 1])

        with col1:
            st.image(poster, caption="Generated Poster Preview", use_container_width=False)

            st.download_button(
                label="Download Poster as PNG",
                data=image_to_bytes(poster),
                file_name="generated_poster.png",
                mime="image/png"
            )

        with col2:
            st.subheader("Poster State")
            st.json(poster_state)

st.divider()

# -------------------------
# Revise poster
# -------------------------
st.subheader("2. Revise the Poster")

revision_prompt = st.text_area(
    "Enter your revision instruction:",
    placeholder="Example: Make it more formal and simpler. Keep the style unchanged.",
    height=110
)

if st.button("Apply Revision"):
    if "poster_state" not in st.session_state:
        st.warning("Please generate a poster first.")
    elif revision_prompt.strip() == "":
        st.warning("Please enter a revision instruction first.")
    else:
        updated_state = revise_poster_state(
            st.session_state["poster_state"],
            revision_prompt
        )

        # Keep current style
        updated_state["style_key"] = st.session_state.get("style_choice", style_choice)

        st.session_state["poster_state"] = updated_state
        poster = generate_poster(updated_state)
        st.session_state["poster"] = poster

        st.success("Revision applied!")

        col1, col2 = st.columns([1.3, 1])

        with col1:
            st.image(poster, caption="Revised Poster Preview", use_container_width=False)

            st.download_button(
                label="Download Revised Poster as PNG",
                data=image_to_bytes(poster),
                file_name="revised_poster.png",
                mime="image/png"
            )

        with col2:
            st.subheader("Updated Poster State")
            st.json(updated_state)

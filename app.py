import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Iterative Poster Agent",
    page_icon="🎨",
    layout="wide"
)


# -----------------------------
# Font loading
# -----------------------------
def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()


# -----------------------------
# Simple prompt parser
# This is rule-based for now.
# Later we will replace this with Gemini API.
# -----------------------------
def parse_prompt(prompt):
    prompt_lower = prompt.lower()

    poster_state = {
        "title": "Poster Draft",
        "subtitle": "Generated from your instruction",
        "body": [
            "This is a simple poster draft.",
            "You can revise the title, color, and text in the next step."
        ],
        "cta": "Learn More",
        "theme": "default"
    }

    if "mid-autumn" in prompt_lower or "mid autumn" in prompt_lower or "moon festival" in prompt_lower:
        poster_state = {
            "title": "Mid-Autumn Festival",
            "subtitle": "Moonlight, reunion, and warm wishes",
            "body": [
                "Celebrate the beauty of the full moon.",
                "Share mooncakes, stories, and joyful moments with family and friends.",
                "Wishing you peace, happiness, and togetherness this season."
            ],
            "cta": "Happy Mid-Autumn Festival",
            "theme": "mid_autumn"
        }

    elif "coffee" in prompt_lower or "latte" in prompt_lower:
        poster_state = {
            "title": "Fresh Coffee Moments",
            "subtitle": "A warm cup for a better day",
            "body": [
                "Enjoy freshly brewed coffee made for your daily pause.",
                "Smooth taste, rich aroma, and a comforting finish.",
                "Perfect for mornings, meetings, and quiet afternoons."
            ],
            "cta": "Try It Today",
            "theme": "coffee"
        }

    elif "market closure" in prompt_lower or "休市" in prompt_lower:
        poster_state = {
            "title": "Market Closure Notice",
            "subtitle": "Important trading arrangement update",
            "body": [
                "Please note the market closure arrangement.",
                "Kindly plan your trading and settlement schedule in advance.",
                "Normal trading will resume according to the official market calendar."
            ],
            "cta": "Please Plan Ahead",
            "theme": "finance"
        }

    elif "recruitment" in prompt_lower or "career" in prompt_lower or "job" in prompt_lower:
        poster_state = {
            "title": "Career Opportunity",
            "subtitle": "Build your future with us",
            "body": [
                "We are looking for motivated and talented individuals.",
                "Join our team to grow, learn, and make an impact.",
                "Submit your application and take the next step."
            ],
            "cta": "Apply Now",
            "theme": "career"
        }

    return poster_state


# -----------------------------
# Theme configuration
# -----------------------------
def get_theme_colors(theme):
    themes = {
        "mid_autumn": {
            "background": "#0F1B2D",
            "card": "#FFF7E6",
            "primary": "#F6D365",
            "text": "#2F241D",
            "accent": "#D99A2B"
        },
        "coffee": {
            "background": "#4B2E2A",
            "card": "#F7E7CE",
            "primary": "#F2D2A9",
            "text": "#3A241F",
            "accent": "#A76F4D"
        },
        "finance": {
            "background": "#102A43",
            "card": "#F8FAFC",
            "primary": "#D4AF37",
            "text": "#1F2933",
            "accent": "#B8860B"
        },
        "career": {
            "background": "#1E3A5F",
            "card": "#F4F8FB",
            "primary": "#BFD7EA",
            "text": "#1F2933",
            "accent": "#2E86AB"
        },
        "default": {
            "background": "#2F3A4A",
            "card": "#FFFFFF",
            "primary": "#F2D6A2",
            "text": "#333333",
            "accent": "#6B7280"
        }
    }

    return themes.get(theme, themes["default"])


# -----------------------------
# Poster rendering
# -----------------------------
def generate_poster(poster_state):
    width, height = 1080, 1350
    colors = get_theme_colors(poster_state["theme"])

    img = Image.new("RGB", (width, height), color=colors["background"])
    draw = ImageDraw.Draw(img)

    title_font = load_font(72, bold=True)
    subtitle_font = load_font(34)
    body_font = load_font(34)
    cta_font = load_font(42, bold=True)
    footer_font = load_font(24)

    # Decorative elements for Mid-Autumn
    if poster_state["theme"] == "mid_autumn":
        # Moon
        draw.ellipse([760, 90, 980, 310], fill="#F9E7A1")
        draw.ellipse([710, 80, 930, 300], fill=colors["background"])

        # Small stars
        for x, y in [(130, 120), (220, 230), (930, 430), (820, 520), (160, 470)]:
            draw.ellipse([x, y, x + 8, y + 8], fill="#F6D365")

    # Header text
    draw.text((80, 120), poster_state["title"], fill=colors["primary"], font=title_font)
    draw.text((84, 220), poster_state["subtitle"], fill="#FFFFFF", font=subtitle_font)

    # Main card
    card_x1, card_y1 = 80, 390
    card_x2, card_y2 = width - 80, height - 180

    draw.rounded_rectangle(
        [card_x1, card_y1, card_x2, card_y2],
        radius=40,
        fill=colors["card"]
    )

    # Body text
    y = card_y1 + 90
    for paragraph in poster_state["body"]:
        wrapped_lines = textwrap.wrap(paragraph, width=42)
        for line in wrapped_lines:
            draw.text((card_x1 + 70, y), line, fill=colors["text"], font=body_font)
            y += 48
        y += 28

    # CTA block
    draw.rounded_rectangle(
        [card_x1 + 70, card_y2 - 170, card_x2 - 70, card_y2 - 70],
        radius=28,
        fill=colors["accent"]
    )

    draw.text(
        (card_x1 + 100, card_y2 - 145),
        poster_state["cta"],
        fill="#FFFFFF",
        font=cta_font
    )

    # Footer
    draw.text(
        (80, height - 90),
        "Iterative Poster Agent · Prototype v0.2",
        fill="#FFFFFF",
        font=footer_font
    )

    return img


# -----------------------------
# Convert image to downloadable bytes
# -----------------------------
def image_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🎨 Iterative Poster Agent")

st.write(
    "A prototype tool for generating and revising simple posters based on natural language instructions."
)

st.divider()

st.subheader("Create a Poster")

user_prompt = st.text_area(
    "Enter your poster instruction:",
    placeholder="Example: create a simple Mid-Autumn Festival poster",
    height=120
)

if st.button("Generate Poster"):
    if user_prompt.strip() == "":
        st.warning("Please enter a poster instruction first.")
    else:
        poster_state = parse_prompt(user_prompt)
        st.session_state["poster_state"] = poster_state

        poster = generate_poster(poster_state)
        st.session_state["poster"] = poster

        st.success("Poster generated!")

        st.image(poster, caption="Generated Poster Preview", use_container_width=False)

        st.download_button(
            label="Download Poster as PNG",
            data=image_to_bytes(poster),
            file_name="generated_poster.png",
            mime="image/png"
        )

        with st.expander("View poster state JSON"):
            st.json(poster_state)

st.divider()

st.subheader("Revise the Poster")

revision_prompt = st.text_area(
    "Enter your revision instruction:",
    placeholder="Example: Make it more formal / Change the theme to coffee / Make the title about reunion.",
    height=100
)

if st.button("Apply Revision"):
    if "poster_state" not in st.session_state:
        st.warning("Please generate a poster first.")
    elif revision_prompt.strip() == "":
        st.warning("Please enter a revision instruction first.")
    else:
        poster_state = st.session_state["poster_state"]
        revision_lower = revision_prompt.lower()

        # Simple revision logic for now
        if "formal" in revision_lower:
            poster_state["theme"] = "finance"
            poster_state["subtitle"] = "A refined and professional visual update"

        if "coffee" in revision_lower:
            poster_state["theme"] = "coffee"
            poster_state["title"] = "Fresh Coffee Moments"

        if "reunion" in revision_lower:
            poster_state["title"] = "A Season of Reunion"
            poster_state["subtitle"] = "Under the same moon, we gather in warmth"

        if "simple" in revision_lower or "minimal" in revision_lower:
            poster_state["body"] = [
                "A clean and warm poster design.",
                "Focused on the key message with a simple visual style."
            ]

        st.session_state["poster_state"] = poster_state
        poster = generate_poster(poster_state)
        st.session_state["poster"] = poster

        st.success("Revision applied!")

        st.image(poster, caption="Revised Poster Preview", use_container_width=False)

        st.download_button(
            label="Download Revised Poster as PNG",
            data=image_to_bytes(poster),
            file_name="revised_poster.png",
            mime="image/png"
        )

        with st.expander("View updated poster state JSON"):
            st.json(poster_state)

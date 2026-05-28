import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO


st.set_page_config(
    page_title="Iterative Poster Agent",
    page_icon="🎨",
    layout="wide"
)


def generate_simple_poster(user_prompt):
    width, height = 1080, 1350

    # Create background
    img = Image.new("RGB", (width, height), color="#F7F0E8")
    draw = ImageDraw.Draw(img)

    # Use default fonts first for deployment stability
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    # Poster content
    title = "Poster Draft"
    subtitle = "Generated from your instruction"
    body = user_prompt

    # Decorative header block
    draw.rectangle([0, 0, width, 220], fill="#2F3A4A")

    # Text
    draw.text((80, 80), title, fill="white", font=title_font)
    draw.text((80, 140), subtitle, fill="#F2D6A2", font=body_font)

    # Main content card
    draw.rounded_rectangle(
        [80, 320, width - 80, height - 180],
        radius=35,
        fill="white"
    )

    draw.text((120, 380), "User Instruction", fill="#2F3A4A", font=title_font)

    wrapped_text = textwrap.wrap(body, width=55)
    y = 460

    for line in wrapped_text:
        draw.text((120, y), line, fill="#333333", font=body_font)
        y += 35

    # Footer
    draw.text(
        (80, height - 100),
        "Iterative Poster Agent · Prototype",
        fill="#666666",
        font=body_font
    )

    return img


def image_to_bytes(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


st.title("🎨 Iterative Poster Agent")

st.write(
    "A simple prototype for generating and revising posters based on natural language instructions."
)

st.divider()

st.subheader("Create a Poster")

user_prompt = st.text_area(
    "Enter your poster instruction:",
    placeholder="Example: Create a formal market closure notice poster in Traditional Chinese.",
    height=120
)

if st.button("Generate Poster"):
    if user_prompt.strip() == "":
        st.warning("Please enter a poster instruction first.")
    else:
        st.success("Poster generated!")

        poster = generate_simple_poster(user_prompt)

        st.image(poster, caption="Generated Poster Preview", use_container_width=False)

        st.download_button(
            label="Download Poster as PNG",
            data=image_to_bytes(poster),
            file_name="generated_poster.png",
            mime="image/png"
        )

st.divider()

st.subheader("Revise the Poster")

revision_prompt = st.text_area(
    "Enter your revision instruction:",
    placeholder="Example: Make the title larger and change the body text to Traditional Chinese.",
    height=100
)

if st.button("Apply Revision"):
    if revision_prompt.strip() == "":
        st.warning("Please enter a revision instruction first.")
    else:
        st.info(
            "Revision function will be connected in the next version. "
            "For now, this prototype only generates the initial poster."
        )
        st.write(revision_prompt)

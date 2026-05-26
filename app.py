import streamlit as st

st.set_page_config(
    page_title="Iterative Poster Agent",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Iterative Poster Agent")

st.write("This is a simple prototype for generating and revising posters based on natural language instructions.")

st.subheader("Create a Poster")

user_prompt = st.text_area(
    "Enter your poster instruction:",
    placeholder="Example: Create a formal market closure notice poster in Traditional Chinese."
)

if st.button("Generate Poster"):
    if user_prompt:
        st.success("Instruction received!")
        st.write(user_prompt)
    else:
        st.warning("Please enter an instruction first.")

st.subheader("Revise the Poster")

revision_prompt = st.text_area(
    "Enter your revision instruction:",
    placeholder="Example: Make the title larger and change the body text to Traditional Chinese."
)

if st.button("Apply Revision"):
    if revision_prompt:
        st.success("Revision received!")
        st.write(revision_prompt)
    else:
        st.warning("Please enter a revision instruction first.")

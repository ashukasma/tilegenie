"""
TileGenie - Minimal Test Version
"""

import streamlit as st
import os

st.set_page_config(
    page_title="TileGenie",
    page_icon="🟦",
    layout="wide"
)

st.title("🟦 TileGenie - Test Version")
st.write("If you see this page, the app is working!")

genie_space_id = os.getenv("GENIE_SPACE_ID", "Not configured")
st.write(f"**Genie Space ID:** {genie_space_id}")

st.success("✅ App infrastructure is healthy!")
st.balloons()

st.write("---")
st.write("### Status Check:")
st.write("- ✅ Streamlit running")
st.write("- ✅ Environment variables loaded")
st.write("- ✅ No crashes!")

if st.button("Click Me!"):
    st.success("Button works!")
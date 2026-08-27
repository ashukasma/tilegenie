"""
Minimal Test App - Just Hello World
"""

import streamlit as st

st.set_page_config(page_title="Test", page_icon="✅")

st.title("✅ TileGenie Test")
st.write("If you can see this, the Databricks App is working!")
st.write("The issue was with the Genie integration code.")

st.balloons()

st.write("---")
st.write("### App Info:")
import os
st.write(f"- Genie Space ID: {os.getenv('GENIE_SPACE_ID', 'Not set')}")
st.write("- This test has NO Databricks SDK")
st.write("- This test has NO Genie code")
st.write("- Just pure Streamlit")
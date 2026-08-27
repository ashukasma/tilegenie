"""
TileGenie with Health Check Endpoint
"""

import streamlit as st
import os

st.set_page_config(
    page_title="TileGenie",
    page_icon="🟦",
    layout="wide"
)

# Simple health check message at the top
st.sidebar.success("✅ App is running!")

st.title("🟦 TileGenie")
st.write("Production Intelligence - Minimal Version")

genie_space_id = os.getenv("GENIE_SPACE_ID", "Not configured")
st.write(f"**Genie Space ID:** {genie_space_id[:8]}..." if len(genie_space_id) > 8 else genie_space_id)

st.info("This is a simplified version to test connectivity. Full Genie integration coming next.")

# Test button
if st.button("Test Connection"):
    st.balloons()
    st.success("✅ Connection test successful!")
    st.write("If you see this, the app infrastructure is working!")

st.write("---")
st.write("### Next Steps:")
st.write("1. Verify this minimal version works")
st.write("2. Add back Databricks SDK")
st.write("3. Add back Genie integration")

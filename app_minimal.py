"""
Minimal Test App - Just Hello World
This will help us determine if the issue is with Databricks Apps or with the Genie code
"""

import streamlit as st

st.set_page_config(page_title="Test", page_icon="✅")

st.title("✅ TileGenie Test App")
st.write("If you can see this, the Databricks App is working!")
st.write("The issue is with the Genie integration code.")

st.balloons()

st.write("---")
st.write("### Next Steps:")
st.write("1. If this works, we know the app infrastructure is fine")
st.write("2. We can then add back the Genie code piece by piece")
st.write("3. To find exactly what's causing the crash")

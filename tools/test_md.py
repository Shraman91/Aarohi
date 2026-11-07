from streamlit.testing.v1 import AppTest

code = """
import streamlit as st
st.markdown('<div class="wrap"><pre>line1\\nline2\\nline3</pre></div>', unsafe_allow_html=True)
"""

at = AppTest.from_string(code)
at.run()
print("AppTest markdown value:")
print(repr(at.markdown[0].value))


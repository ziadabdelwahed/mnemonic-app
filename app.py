import streamlit as st
from main import MnemonicEngine

st.title("Bitcoin Key Generator 💻")

# 👇 تقسيم الصفحة لأعمدة (أزرار جنب بعض)
col1, col2, col3, col4, col5 = st.columns(5)

result = None

if col1.button("12 كلمة"):
    result = MnemonicEngine.generate(128)

if col2.button("15 كلمة"):
    result = MnemonicEngine.generate(160)

if col3.button("18 كلمة"):
    result = MnemonicEngine.generate(192)

if col4.button("21 كلمة"):
    result = MnemonicEngine.generate(224)

if col5.button("24 كلمة"):
    result = MnemonicEngine.generate(256)

# 👇 عرض النتيجة
if result:
    words = result.mnemonic.split()

    clean_text = " ".join(words)

    st.code(clean_text, language="text")

import streamlit as st
from main import MnemonicEngine

st.title("Bitcoin Key Generator 💻")

if st.button("Generate 12 Words"):
    result = MnemonicEngine.generate(128)

    words = result.mnemonic.split()

    # 👇 نجمع الكلمات بدون أرقام
    clean_text = " ".join(words[:12])

    # 👇 عرض بشكل كود + زر Copy
    st.code(clean_text, language="text")

import streamlit as st
from main import MnemonicEngine

st.title("Mnemonic Generator 💻")

if st.button("Generate 12 Words"):
    result = MnemonicEngine.generate(128)  # 👈 بيرجع object

    words = result.mnemonic.split()  # 👈 الصح هنا

    for i, word in enumerate(words[:12], 1):
        st.write(f"{i}- {word}")

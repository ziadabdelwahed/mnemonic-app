import streamlit as st
from main import MnemonicEngine

st.title("Mnemonic Generator 💻")

if st.button("Generate 12 Words"):
    result = MnemonicEngine.generate(128)

    mnemonic_text = str(result.mnemonic)  # 👈 نحوله نص غصب عنه

    words = mnemonic_text.split()

    for i, word in enumerate(words[:12], 1):
        st.write(f"{i}- {word}")

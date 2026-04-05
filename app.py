import streamlit as st
from main import MnemonicEngine

st.title("Mnemonic Generator 💻")

engine = MnemonicEngine()  # 👈 دي أهم سطر

if st.button("Generate 12 Words"):
    words = engine.generate(128).split()

    for i, word in enumerate(words[:12], 1):
        st.write(f"{i}- {word}")


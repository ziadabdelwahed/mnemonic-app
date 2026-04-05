import streamlit as st
from main import MnemonicEngine

st.title("Bitcoin Key Generator 💻")

# 👇 تقسيم الصفحة لأعمدة (أزرار جنب بعض)
col1, col2, col3, col4, col5 = st.columns(5)

result = None

if col1.button("12 words"):
    result = MnemonicEngine.generate(128)

if col2.button("15 words"):
    result = MnemonicEngine.generate(160)

if col3.button("18 words"):
    result = MnemonicEngine.generate(192)

if col4.button("21 words"):
    result = MnemonicEngine.generate(224)

if col5.button("24 words"):
    result = MnemonicEngine.generate(256)

# 👇 عرض النتيجة
if result:
    words = result.mnemonic.split()

    clean_text = " ".join(words)

    st.code(clean_text, language="text")






<svg xmlns="http://www.w3.org/2000/svg" width="256" height="254" viewBox="0 0 256 254">
<!-- SVG created with Arrow, by QuiverAI (https://quiver.ai) -->
  <path d="m255 128c0 69.93-57.27 126-127.3 126-70.03 0-126.7-56.04-126.7-126 0-69.92 56.69-127 126.7-127 70.02 0 127.3 56.13 127.3 127z" fill="#F29216" stroke="#CCEAD9" stroke-miterlimit="10" stroke-width=".5669"/>
  <path d="m183.2 105.9c2.23-16.41-10.35-25.36-29.55-32.12l4.35-23.73-13.29-2.71-4.35 23.12c-3.63-0.75-7.41-1.46-11.11-2.18l3.68-23.3-13.29-2.71-4.64 23.68c-3.02-0.61-6-1.22-8.89-1.88l0.02-0.1-19.2-4-2.8 14.35s10.14 2.04 9.88 2.23c5.55 1.2 6.48 4.93 6.2 7.93l-4 21.34c0.39 0.08 0.88 0.23 1.42 0.47-0.44-0.1-0.93-0.22-1.44-0.3l-9.16 46.22c-0.66 2.03-2.39 5.09-6.85 4.06 0.2 0.26-9.85-2.08-9.85-2.08l-5.8 17.74 18.58 4.1c2.98 0.71 5.96 1.48 8.89 2.14l-4.34 22.63 15.07 2.7 4.35-22.78c3.78 0.98 7.41 1.92 10.99 2.63l-4.35 22.62 14.35 2.71 4.39-23.17c23.48 3.36 41.17 0.41 47.93-19.91 5.95-15.55-0.15-26.6-14.15-37.16 9.56-2.43 15.41-9.54 16.96-22.54zm-29.85 48.46c-4 16.06-28.3 12.38-43.37 8.85l7.01-34.2c15.06 3.26 40.86 7.61 36.36 25.35zm2.51-48.71c-3.53 14.4-23.22 11.59-35.95 8.69l5.35-28.99c12.73 2.71 34.47 5.04 30.6 20.3z" fill="#FEFFFE"/>
</svg>
